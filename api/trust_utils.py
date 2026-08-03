"""Trust card and bucket lookup for API responses."""

from __future__ import annotations

from typing import Any

from engine.backtest import score_bucket


def bucket_for_verdict(action: str, weighted_score: float) -> str | None:
    if action == "NO_TRADE":
        return None
    return score_bucket(weighted_score, action)


def walk_forward_summary(wf: Any) -> dict[str, Any]:
    if not isinstance(wf, list) or not wf:
        return {"passed": None, "symbols": 0, "detail": []}
    passed_all = all(bool(item.get("accepted")) for item in wf if isinstance(item, dict))
    return {
        "passed": passed_all,
        "symbols": len(wf),
        "detail": [
            {
                "symbol": item.get("symbol"),
                "accepted": item.get("accepted"),
                "out_of_sample_profit_factor": item.get("out_of_sample_profit_factor"),
            }
            for item in wf
            if isinstance(item, dict)
        ],
    }


def trust_payload(
    *,
    action: str,
    weighted_score: float,
    confidence: str,
    buckets: dict[str, dict],
    walk_forward: Any,
    data_as_of_utc: str,
    last_calibrated_utc: str,
) -> dict[str, Any]:
    bucket = bucket_for_verdict(action, weighted_score)
    stats = buckets.get(bucket, {}) if bucket else {}
    wf = walk_forward_summary(walk_forward)

    return {
        "confidence": confidence,
        "score_bucket": bucket,
        "historical_win_rate": stats.get("win_rate"),
        "backtested_trades": stats.get("trade_count"),
        "profit_factor": stats.get("profit_factor"),
        "average_r": stats.get("avg_r"),
        "max_drawdown_r": stats.get("max_drawdown_r"),
        "walk_forward_passed": wf["passed"],
        "walk_forward": wf,
        "last_calibrated_utc": last_calibrated_utc or "never",
        "data_as_of_utc": data_as_of_utc,
    }
