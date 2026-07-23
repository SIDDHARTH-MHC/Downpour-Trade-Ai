"""Map backtest stats to confidence labels."""

from __future__ import annotations

import json
from pathlib import Path

from engine.config import EngineConfig, load_config
from engine.models import Verdict


def _score_bucket(score: float, action: str) -> str:
    s = score if action == "LONG" else abs(score)
    if s >= 50:
        return "50+"
    if s >= 35:
        return "35-50"
    return "35-50"


def load_calibration_tables(path: Path | None = None) -> dict:
    cal_path = path or Path("data/calibration.json")
    if not cal_path.exists():
        return {}
    return json.loads(cal_path.read_text())


def calibrate_label(verdict: Verdict, tables: dict | None = None, config: EngineConfig | None = None) -> str:
    cfg = (config or load_config()).calibration
    tables = tables if tables is not None else load_calibration_tables()

    if verdict.action == "NO_TRADE":
        return "N/A"

    bucket = _score_bucket(abs(verdict.weighted_score), verdict.action)
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
    from engine.backtest import run_backtest, save_calibration_data

    cfg = config or load_config()
    results = [run_backtest(sym, tf, months, cfg) for sym in symbols]
    return save_calibration_data(results, Path(cfg.data.cache_dir) / "calibration.json")
