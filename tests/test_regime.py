from engine.lanes.regime import analyze_regime
from tests.conftest import make_ohlcv


def test_regime_shock_on_high_volatility():
    df = make_ohlcv(n=500, trend=0.05, noise=0.02)
    result = analyze_regime(df, df, "BTC/USDT", tf="1h")
    assert result.regime in {"SHOCK", "TRENDING_UP", "TRENDING_DOWN", "RANGING", "COMPRESSION"}
    assert len(result.evidence) > 0


def test_regime_btc_filter_blocks_alts():
    df = make_ohlcv(n=50)
    btc = make_ohlcv(n=50, trend=0.03, noise=0.0)
    result = analyze_regime(df, df, "SOL/USDT", btc_df=btc, tf="1h")
    assert result.tradeable is False
