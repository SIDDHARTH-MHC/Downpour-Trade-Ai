import pandas as pd

from research_platform.dq.scanner import scan_ohlcv_frame
from research_platform.hashes import dataset_hash, feature_manifest_hash, universe_hash
from tests.conftest import make_ohlcv


def test_universe_hash_stable():
    u = {"symbols": ["BTC/USDT", "ETH/USDT"], "tier": "T1"}
    assert universe_hash(u) == universe_hash(u)


def test_feature_manifest_hash():
    m = {"structure_degraded": True, "order_book": False}
    assert len(feature_manifest_hash(m)) == 64


def test_dq_scan_clean_trend():
    df = make_ohlcv(n=100, trend=0.001, noise=0.0001)
    report = scan_ohlcv_frame(df, symbol="BTC/USDT", timeframe="1h")
    assert report["severity"] in {"ok", "warning", "blocking"}
    assert "duplicate_bars" in report


def test_market_data_repository_live_fallback():
    from research_platform.repository.market_data import MarketDataRepository

    repo = MarketDataRepository()
    assert repo.history_enabled() is False
    df = repo.history_candles("BTC/USDT", "1h", limit=50)
    assert isinstance(df, pd.DataFrame)
