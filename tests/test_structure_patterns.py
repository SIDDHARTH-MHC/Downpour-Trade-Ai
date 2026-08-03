import pandas as pd

from engine.structure_patterns import cluster_levels, detect_fvg, detect_liquidity_sweep


def test_liquidity_sweep_bullish_synthetic():
    n = 25
    rows = []
    for _ in range(n - 1):
        rows.append({"open": 100.0, "high": 101.0, "low": 100.0, "close": 100.5, "volume": 10.0})
    rows.append({"open": 100.0, "high": 100.8, "low": 98.8, "close": 100.6, "volume": 50.0})
    df = pd.DataFrame(rows)
    sweep = detect_liquidity_sweep(df, lookback=20, require_volume=False)
    assert sweep is not None
    assert sweep["direction"] == "bullish"


def test_equal_pct_cluster_merges():
    pts = [100.0, 100.05, 110.0]
    out = cluster_levels(pts, atr=1.0, factor=0.01, equal_pct=0.001)
    assert len(out) == 2


def test_fvg_bullish_gap():
    rows = [
        {"open": 99, "high": 100, "low": 98, "close": 99.5, "volume": 1},
        {"open": 99.5, "high": 100, "low": 99, "close": 99.8, "volume": 1},
        {"open": 101, "high": 102, "low": 101, "close": 101.5, "volume": 1},
    ]
    df = pd.DataFrame(rows)
    fvg = detect_fvg(df, min_gap_atr=0.0, atr=1.0)
    assert fvg is not None
    assert fvg["direction"] == "bullish"
