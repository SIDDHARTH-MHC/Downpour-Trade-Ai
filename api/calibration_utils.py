"""Helpers to separate score-bucket stats from calibration metadata."""

from __future__ import annotations

from typing import Any


def is_bucket_stats(value: Any) -> bool:
    return isinstance(value, dict) and "trade_count" in value and "win_rate" in value


def filter_calibration_buckets(stats: dict[str, Any]) -> dict[str, dict]:
    return {key: value for key, value in stats.items() if is_bucket_stats(value)}
