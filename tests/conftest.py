"""Shared synthetic fixtures for tests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def make_ohlcv(n: int = 500, trend: float = 0.002, start: float = 100.0, noise: float = 0.001) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    prices = [start]
    for _ in range(n - 1):
        prices.append(prices[-1] * (1 + trend + rng.normal(0, noise)))

    close = np.array(prices)
    high = close * (1 + abs(rng.normal(0, 0.002, n)))
    low = close * (1 - abs(rng.normal(0, 0.002, n)))
    open_ = np.roll(close, 1)
    open_[0] = start
    volume = rng.uniform(1000, 5000, n)
    ts = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC").astype("int64") // 10**6

    return pd.DataFrame(
        {
            "timestamp": ts,
            "open": open_.astype("float64"),
            "high": high.astype("float64"),
            "low": low.astype("float64"),
            "close": close.astype("float64"),
            "volume": volume.astype("float64"),
        }
    )


def make_chop_ohlcv(n: int = 500) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    base = 100.0
    close = base + np.sin(np.linspace(0, 40 * np.pi, n)) * 0.15
    high = close + abs(rng.normal(0, 0.3, n))
    low = close - abs(rng.normal(0, 0.3, n))
    open_ = np.roll(close, 1)
    open_[0] = base
    volume = rng.uniform(1000, 5000, n)
    ts = pd.date_range("2024-01-01", periods=n, freq="h", tz="UTC").astype("int64") // 10**6
    return pd.DataFrame(
        {
            "timestamp": ts,
            "open": open_.astype("float64"),
            "high": high.astype("float64"),
            "low": low.astype("float64"),
            "close": close.astype("float64"),
            "volume": volume.astype("float64"),
        }
    )
