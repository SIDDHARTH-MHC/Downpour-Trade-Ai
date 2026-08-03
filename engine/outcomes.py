"""Resolve open signal outcomes from OHLCV without look-ahead."""

from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd


def verdict_bar_timestamp_ms(payload: dict) -> int | None:
    """Last closed bar time on the verdict (ms), from engine `timestamp` field."""
    raw = payload.get("timestamp")
    if not raw or not isinstance(raw, str):
        return None
    text = raw.replace(" UTC", "").strip()
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(text, fmt).replace(tzinfo=timezone.utc)
            return int(dt.timestamp() * 1000)
        except ValueError:
            continue
    return None


def resolve_outcome_after_signal(
    df: pd.DataFrame,
    *,
    action: str,
    stop_loss: float,
    tp1: float,
    signal_bar_ms: int,
) -> str | None:
    """
    Walk forward only bars strictly after the signal candle open time.
    Signal is formed at that bar's close — same-bar high/low are excluded.
    """
    if df.empty or "timestamp" not in df.columns:
        return None

    forward = df[df["timestamp"].astype("int64") > signal_bar_ms]
    if forward.empty:
        return None

    for _, row in forward.iterrows():
        high, low = float(row["high"]), float(row["low"])
        if action == "LONG":
            if low <= stop_loss:
                return "SL"
            if high >= tp1:
                return "TP1"
        elif action == "SHORT":
            if high >= stop_loss:
                return "SL"
            if low <= tp1:
                return "TP1"
    return None
