"""Map backtest stats to confidence labels."""

from __future__ import annotations

import json
from pathlib import Path

from engine.config import EngineConfig, load_config
from engine.models import Verdict
from engine.score_buckets import score_bucket


def load_calibration_tables(path: Path | None = None) -> dict:
    cal_path = path or Path("data/calibration.json")
    if not cal_path.exists():
        return {}
    data = json.loads(cal_path.read_text())
    # Strip walk_forward metadata when looking up buckets
    return {k: v for k, v in data.items() if k != "walk_forward" and isinstance(v, dict)}


def calibrate_label(verdict: Verdict, tables: dict | None = None, config: EngineConfig | None = None) -> str:
    cfg = (config or load_config()).calibration
    tables = tables if tables is not None else load_calibration_tables()

    if verdict.action == "NO_TRADE":
        return "N/A"

    bucket = score_bucket(verdict.weighted_score, verdict.action)
    stats = tables.get(bucket)
    if not stats:
        return "confidence: INSUFFICIENT_DATA (no backtest bucket)"

    n = stats.get("trade_count", 0)
    win_rate = stats.get("win_rate", 0)
    pf = stats.get("profit_factor", 0)

    if n < cfg.insufficient_data_trades:
        return f"confidence: INSUFFICIENT_DATA (n={n} historical trades)"

    if win_rate >= cfg.high_win_rate and n >= cfg.high_min_trades and pf >= cfg.high_profit_factor:
        return f"HIGH (win_rate={win_rate*100:.1f}%, n={n}, PF={pf:.2f})"

    if win_rate >= cfg.moderate_win_rate and n >= cfg.moderate_min_trades and pf >= cfg.moderate_profit_factor:
        return f"MODERATE (win_rate={win_rate*100:.1f}%, n={n}, PF={pf:.2f})"

    return f"LOW (win_rate={win_rate*100:.1f}%, n={n}, PF={pf:.2f})"


def apply_confidence(verdict: Verdict, config: EngineConfig | None = None) -> Verdict:
    verdict.confidence = calibrate_label(verdict, config=config)
    return verdict


def rebuild_calibration(symbols: list[str], tf: str, months: int, config: EngineConfig | None = None) -> dict:
    from engine.backtest import BacktestResult, bucket_stats_from_trades, run_walk_forward, save_calibration_data

    cfg = config or load_config()
    all_oos_trades = []
    wf_reports = []

    for sym in symbols:
        wf = run_walk_forward(sym, tf, months, cfg)
        wf_reports.append({"symbol": sym, **{k: v for k, v in wf.items() if k != "oos_trades"}})
        all_oos_trades.extend(wf.get("oos_trades", []))

    pseudo = BacktestResult(symbol=",".join(symbols), timeframe=tf, trades=all_oos_trades)
    stats = bucket_stats_from_trades(pseudo.trades)
    out_path = Path(cfg.data.cache_dir) / "calibration.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**stats, "walk_forward": wf_reports}
    out_path.write_text(json.dumps(payload, indent=2))
    return payload
