"""Shared utilities for OHLCV manipulation."""

from __future__ import annotations

import pandas as pd

from engine.data import TIMEFRAME_MS


def resample_ohlcv(df: pd.DataFrame, factor: int) -> pd.DataFrame:
    """Downsample OHLCV by grouping every `factor` bars (no lookahead)."""
    if factor <= 1 or df.empty:
        return df.copy()

    rows: list[dict[str, float]] = []
    for start in range(0, len(df), factor):
        chunk = df.iloc[start : start + factor]
        if chunk.empty:
            continue
        rows.append(
            {
                "timestamp": float(chunk["timestamp"].iloc[-1]),
                "open": float(chunk["open"].iloc[0]),
                "high": float(chunk["high"].max()),
                "low": float(chunk["low"].min()),
                "close": float(chunk["close"].iloc[-1]),
                "volume": float(chunk["volume"].sum()),
            }
        )
    return pd.DataFrame(rows)


def htf_factor(ltf: str, htf: str) -> int:
    if ltf not in TIMEFRAME_MS or htf not in TIMEFRAME_MS:
        return 4
    return max(1, TIMEFRAME_MS[htf] // TIMEFRAME_MS[ltf])


def lookback_bars_for_days(tf: str, days: int) -> int:
    ms = TIMEFRAME_MS.get(tf, 3_600_000)
    bars_per_day = 86_400_000 // ms
    return days * bars_per_day
