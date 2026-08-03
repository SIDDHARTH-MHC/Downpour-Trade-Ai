from __future__ import annotations

import asyncio
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from api.alerts import alert_scan_hits
from api.db import Database
from api.settings import get_settings
from api.verdict_enrich import enrich_verdict_payload
from engine.analyzer import analyze_symbol
from engine.calibration import rebuild_calibration
from engine.config import load_config
from engine.data import DataLayer
from engine.outcomes import resolve_outcome_after_signal, verdict_bar_timestamp_ms
from engine.scan_report import summarize_scan

logger = logging.getLogger("downpour.scheduler")
_scheduler: BackgroundScheduler | None = None
_scan_lock = threading.Lock()
_scan_running = False


def scan_status() -> dict:
    db = Database()
    return {
        "running": _scan_running,
        "last_scan_utc": db.get_meta("last_scan_utc", "never"),
        "progress": db.get_meta("scan_progress", ""),
    }


def _resolve_open_outcomes(db: Database) -> None:
    data = DataLayer()
    for item in db.open_outcomes():
        payload = item["payload"]
        plan = payload.get("trade_plan")
        if not plan:
            continue
        signal_ms = verdict_bar_timestamp_ms(payload)
        if signal_ms is None:
            logger.warning("outcome skip %s: missing verdict timestamp", payload.get("symbol"))
            continue
        symbol = payload["symbol"]
        tf = payload["timeframe"]
        try:
            df = data.get_ohlcv(symbol, tf, bars=120, validate=False)
        except Exception as exc:  # noqa: BLE001
            logger.warning("outcome check failed for %s: %s", symbol, exc)
            continue
        outcome = resolve_outcome_after_signal(
            df,
            action=payload["action"],
            stop_loss=float(plan["stop_loss"]),
            tp1=float(plan["tp1"]),
            signal_bar_ms=signal_ms,
        )
        if outcome:
            db.resolve_outcome(item["outcome_id"], outcome)


def _scan_symbol(symbol: str, tf: str, *, light: bool, config, db: Database) -> tuple[str, dict | None]:
    try:
        verdict = analyze_symbol(symbol, tf, light=light, config=config)
        payload = verdict.to_dict()
        payload["data_as_of_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        enrich_verdict_payload(payload, db)
        return symbol, payload
    except Exception as exc:  # noqa: BLE001
        logger.warning("scan skip %s: %s", symbol, exc)
        return symbol, None


def run_scan(tf: str = "1h", limit: int | None = None) -> list[dict]:
    global _scan_running
    settings = get_settings()
    pair_limit = limit or settings.scan_pair_limit

    if not _scan_lock.acquire(blocking=False):
        logger.info("scan already running, skipping")
        return Database().latest_scan(tf)

    _scan_running = True
    try:
        db = Database()
        config = load_config()
        data = DataLayer(config)
        pairs = data.get_top_volume_pairs(min(pair_limit, settings.top_pairs_count))
        results: list[dict] = []
        hits: list[dict] = []
        light = settings.scan_light_mode
        workers = max(1, settings.scan_workers)

        logger.info(
            "starting scan: %s pairs @ %s (light=%s, workers=%s)",
            len(pairs),
            tf,
            light,
            workers,
        )

        # Warm BTC cache once for alt regime checks
        try:
            data.get_ohlcv("BTC/USDT", "1h", bars=10, validate=False)
        except Exception:
            pass

        completed = 0
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_scan_symbol, symbol, tf, light=light, config=config, db=db): symbol
                for symbol in pairs
            }
            for fut in as_completed(futures):
                symbol, payload = fut.result()
                completed += 1
                db.set_meta("scan_progress", f"{completed}/{len(pairs)}:{symbol}")
                if payload is None:
                    continue
                db.save_verdict(payload)
                results.append(payload)
                db.save_scan(tf, results)
                if payload["action"] != "NO_TRADE":
                    hits.append(payload)

        db.save_scan(tf, results)
        report = summarize_scan(results)
        db.set_meta("last_scan_report", json.dumps(report))
        db.set_meta("last_scan_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
        db.set_meta("scan_progress", "done")
        try:
            asyncio.run(alert_scan_hits(hits))
        except Exception as exc:  # noqa: BLE001
            logger.warning("telegram alert failed: %s", exc)
        logger.info("scan complete: %s results", len(results))
        return results
    finally:
        _scan_running = False
        _scan_lock.release()


def run_scan_async(tf: str = "1h", limit: int | None = None) -> None:
    thread = threading.Thread(target=run_scan, kwargs={"tf": tf, "limit": limit}, daemon=True)
    thread.start()


def refresh_pairs() -> None:
    settings = get_settings()
    db = Database()
    data = DataLayer()
    tickers = data.spot.fetch_tickers()
    pairs = [
        (sym, float(info.get("quoteVolume") or 0))
        for sym, info in tickers.items()
        if sym.endswith("/USDT") and info.get("quoteVolume")
    ]
    pairs.sort(key=lambda x: x[1], reverse=True)
    db.save_pairs(pairs[: settings.top_pairs_count])
    db.set_meta("pairs_refreshed_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))


_calibrate_lock = threading.Lock()
_calibrate_running = False


def calibration_status() -> dict:
    db = Database()
    return {
        "running": _calibrate_running,
        "progress": db.get_meta("calibrate_progress", ""),
        "last_calibrated_utc": db.get_meta("last_calibrated_utc", "never"),
        "last_error": db.get_meta("calibrate_error", ""),
    }


def run_calibration_sync(symbols: list[str], tf: str, months: int) -> dict:
    global _calibrate_running
    if not _calibrate_lock.acquire(blocking=False):
        db = Database()
        return db.load_calibration()

    _calibrate_running = True
    db = Database()
    try:
        db.set_meta("calibrate_progress", f"starting:{','.join(symbols)}")
        db.set_meta("calibrate_error", "")
        stats = rebuild_calibration(symbols, tf, months)
        db.save_calibration(stats)
        db.set_meta("last_calibrated_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
        db.set_meta("calibrate_progress", "done")
        logger.info("calibration complete: %s buckets", len(stats))
        return stats
    except Exception as exc:  # noqa: BLE001
        db.set_meta("calibrate_error", str(exc))
        db.set_meta("calibrate_progress", "failed")
        logger.exception("calibration failed")
        raise
    finally:
        _calibrate_running = False
        _calibrate_lock.release()


def run_calibration_async(symbols: list[str], tf: str, months: int) -> None:
    thread = threading.Thread(
        target=_run_calibration_safe,
        kwargs={"symbols": symbols, "tf": tf, "months": months},
        daemon=True,
    )
    thread.start()


def _run_calibration_safe(symbols: list[str], tf: str, months: int) -> None:
    try:
        run_calibration_sync(symbols, tf, months)
    except Exception:  # noqa: BLE001
        pass


def refresh_calibration() -> None:
    db = Database()
    stats = rebuild_calibration(["BTC/USDT", "ETH/USDT", "SOL/USDT"], "1h", 12)
    db.save_calibration(stats)


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    settings = get_settings()
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(
        run_scan,
        "interval",
        minutes=settings.scan_interval_min,
        id="scan",
        kwargs={"tf": "1h", "limit": settings.scan_pair_limit},
    )
    _scheduler.add_job(refresh_pairs, "interval", hours=24, id="pairs")
    _scheduler.add_job(refresh_calibration, "interval", weeks=1, id="calibration")
    _scheduler.add_job(_resolve_open_outcomes, "interval", minutes=30, id="outcomes", args=[Database()])
    _scheduler.start()
    logger.info("scheduler started")

    run_scan_async(tf="1h", limit=settings.scan_pair_limit)
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
