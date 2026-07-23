from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler

from api.alerts import alert_scan_hits
from api.db import Database
from api.settings import get_settings
from engine.analyzer import analyze_symbol
from engine.calibration import rebuild_calibration
from engine.config import load_config
from engine.data import DataLayer

logger = logging.getLogger("downpour.scheduler")
_scheduler: BackgroundScheduler | None = None


def _resolve_open_outcomes(db: Database) -> None:
    data = DataLayer()
    for item in db.open_outcomes():
        payload = item["payload"]
        plan = payload.get("trade_plan")
        if not plan:
            continue
        symbol = payload["symbol"]
        tf = payload["timeframe"]
        try:
            df = data.get_ohlcv(symbol, tf, bars=60, validate=False)
        except Exception as exc:  # noqa: BLE001
            logger.warning("outcome check failed for %s: %s", symbol, exc)
            continue
        entry = plan["entry"]
        sl = plan["stop_loss"]
        tp1 = plan["tp1"]
        action = payload["action"]
        outcome = None
        for _, row in df.iterrows():
            high, low = row["high"], row["low"]
            if action == "LONG":
                if low <= sl:
                    outcome = "SL"
                    break
                if high >= tp1:
                    outcome = "TP1"
                    break
            else:
                if high >= sl:
                    outcome = "SL"
                    break
                if low <= tp1:
                    outcome = "TP1"
                    break
        if outcome:
            db.resolve_outcome(item["outcome_id"], outcome)


def run_scan(tf: str = "1h") -> list[dict]:
    settings = get_settings()
    db = Database()
    config = load_config()
    data = DataLayer(config)
    pairs = data.get_top_volume_pairs(settings.top_pairs_count)
    results: list[dict] = []
    hits: list[dict] = []

    for symbol in pairs:
        try:
            verdict = analyze_symbol(symbol, tf, config=config)
            payload = verdict.to_dict()
            payload["data_as_of_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            db.save_verdict(payload)
            results.append(payload)
            if payload["action"] != "NO_TRADE":
                hits.append(payload)
        except Exception as exc:  # noqa: BLE001
            logger.warning("scan skip %s: %s", symbol, exc)

    db.save_scan(tf, results)
    db.set_meta("last_scan_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    asyncio.run(alert_scan_hits(hits))
    return results


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
    db.save_pairs(pairs[:50])
    db.set_meta("pairs_refreshed_utc", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))


def refresh_calibration() -> None:
    db = Database()
    stats = rebuild_calibration(["BTC/USDT", "ETH/USDT"], "1h", 12)
    db.save_calibration(stats)
    cal_path = Path("data/calibration.json")
    if cal_path.exists():
        db.save_calibration(json.loads(cal_path.read_text()))


def start_scheduler() -> BackgroundScheduler:
    global _scheduler
    if _scheduler is not None:
        return _scheduler

    settings = get_settings()
    _scheduler = BackgroundScheduler(timezone="UTC")
    _scheduler.add_job(run_scan, "interval", minutes=settings.scan_interval_min, id="scan", kwargs={"tf": "1h"})
    _scheduler.add_job(refresh_pairs, "interval", hours=24, id="pairs")
    _scheduler.add_job(refresh_calibration, "interval", weeks=1, id="calibration")
    _scheduler.add_job(_resolve_open_outcomes, "interval", minutes=30, id="outcomes", args=[Database()])
    _scheduler.start()
    logger.info("scheduler started")
    return _scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler:
        _scheduler.shutdown(wait=False)
        _scheduler = None
