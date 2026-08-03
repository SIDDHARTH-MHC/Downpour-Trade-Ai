"""Market structure events (BOS / CHoCH) from swing logic."""

from __future__ import annotations

import pandas as pd

from engine.lanes.structure import detect_swings


def detect_structure_events(df: pd.DataFrame, fractal: int = 5) -> list[dict]:
    """
    Lightweight structure labels on the last closed bar.
    BOS = break of last swing high/low; CHoCH = break against prior micro-trend.
    """
    if len(df) < fractal * 4:
        return []

    events: list[dict] = []
    price = float(df["close"].iloc[-1])
    prev_close = float(df["close"].iloc[-2])

    swing_highs: list[tuple[int, float]] = []
    swing_lows: list[tuple[int, float]] = []
    n = fractal
    for i in range(n, len(df) - n):
        window_high = df["high"].iloc[i - n : i + n + 1]
        window_low = df["low"].iloc[i - n : i + n + 1]
        if df["high"].iloc[i] == window_high.max():
            swing_highs.append((i, float(df["high"].iloc[i])))
        if df["low"].iloc[i] == window_low.min():
            swing_lows.append((i, float(df["low"].iloc[i])))

    if not swing_highs or not swing_lows:
        return events

    last_sh = swing_highs[-1][1]
    prev_sh = swing_highs[-2][1] if len(swing_highs) >= 2 else last_sh
    last_sl = swing_lows[-1][1]
    prev_sl = swing_lows[-2][1] if len(swing_lows) >= 2 else last_sl

    if prev_close <= last_sh < price:
        events.append(
            {
                "type": "BOS",
                "direction": "bullish",
                "level": last_sh,
                "label": f"Bullish BOS above swing high {last_sh:.4g}",
            }
        )
    if prev_close >= last_sl > price:
        events.append(
            {
                "type": "BOS",
                "direction": "bearish",
                "level": last_sl,
                "label": f"Bearish BOS below swing low {last_sl:.4g}",
            }
        )

    making_hh = last_sh > prev_sh and last_sl > prev_sl
    making_ll = last_sh < prev_sh and last_sl < prev_sl
    if making_hh and price < last_sl:
        events.append(
            {
                "type": "CHoCH",
                "direction": "bearish",
                "level": last_sl,
                "label": f"Bearish CHoCH — break below {last_sl:.4g} after higher highs",
            }
        )
    if making_ll and price > last_sh:
        events.append(
            {
                "type": "CHoCH",
                "direction": "bullish",
                "level": last_sh,
                "label": f"Bullish CHoCH — break above {last_sh:.4g} after lower lows",
            }
        )

    return events
