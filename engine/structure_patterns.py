"""Deterministic structure patterns (Research_Roadmap R2–R4)."""

from __future__ import annotations

from typing import Any

import pandas as pd


def cluster_levels(
    points: list[float],
    atr: float,
    factor: float,
    *,
    equal_pct: float = 0.0,
) -> list[tuple[float, int]]:
    """Cluster swing points; optional merge of equal highs/lows within equal_pct of price."""
    if not points:
        return []
    points = sorted(points)
    if equal_pct > 0:
        merged: list[float] = [points[0]]
        for p in points[1:]:
            ref = merged[-1]
            if ref != 0 and abs(p - ref) / ref <= equal_pct:
                merged[-1] = (ref + p) / 2
            else:
                merged.append(p)
        points = merged

    clusters: list[list[float]] = [[points[0]]]
    threshold = atr * factor
    for p in points[1:]:
        if abs(p - clusters[-1][-1]) <= threshold:
            clusters[-1].append(p)
        else:
            clusters.append([p])
    return [(float(sum(c) / len(c)), len(c)) for c in clusters]


def detect_liquidity_sweep(
    df: pd.DataFrame,
    lookback: int = 20,
    *,
    require_volume: bool = True,
) -> dict[str, Any] | None:
    """
    Bullish sweep: wick below prior lookback low, close reclaims above that low,
    close in upper half of bar. Bearish is symmetric on highs.
    """
    if len(df) < lookback + 2:
        return None

    window = df.iloc[-(lookback + 1) : -1]
    bar = df.iloc[-1]
    low = float(bar["low"])
    high = float(bar["high"])
    close = float(bar["close"])
    vol = float(bar["volume"])

    prior_min = float(window["low"].min())
    prior_max = float(window["high"].max())

    def volume_ok() -> bool:
        if not require_volume or len(df) < 22:
            return True
        avg = float(df["volume"].iloc[-21:-1].mean())
        return vol > avg

    rng = high - low
    if rng > 0:
        upper_half = close >= low + 0.5 * rng
        lower_half = close <= high - 0.5 * rng
    else:
        upper_half = lower_half = False

    if low < prior_min and close > prior_min and upper_half and volume_ok():
        return {
            "direction": "bullish",
            "level": prior_min,
            "label": f"Bullish liquidity sweep below {prior_min:.4g}, reclaimed",
        }

    if high > prior_max and close < prior_max and lower_half and volume_ok():
        return {
            "direction": "bearish",
            "level": prior_max,
            "label": f"Bearish liquidity sweep above {prior_max:.4g}, reclaimed",
        }

    return None


def detect_fvg(df: pd.DataFrame, min_gap_atr: float = 0.0, atr: float = 1.0) -> dict[str, Any] | None:
    """3-candle FVG on last bar (bull: low[i] > high[i-2])."""
    if len(df) < 3:
        return None
    h2 = float(df["high"].iloc[-3])
    l1 = float(df["low"].iloc[-1])
    h0 = float(df["high"].iloc[-2])
    l2 = float(df["low"].iloc[-3])

    gap_min = min_gap_atr * atr if atr > 0 else 0.0

    if l1 > h2 and (l1 - h2) >= gap_min:
        return {
            "direction": "bullish",
            "level": (l1 + h2) / 2,
            "label": f"Bullish FVG gap {h2:.4g}–{l1:.4g}",
        }

    hi = float(df["high"].iloc[-1])
    lo2 = float(df["low"].iloc[-3])
    if hi < lo2 and (lo2 - hi) >= gap_min:
        return {
            "direction": "bearish",
            "level": (lo2 + hi) / 2,
            "label": f"Bearish FVG gap {hi:.4g}–{lo2:.4g}",
        }
    return None
