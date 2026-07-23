import pytest

from engine.data import DataLayer, StaleDataError, TIMEFRAME_MS, _utc_now_ms
from tests.conftest import make_ohlcv


def test_stale_data_raises():
    df = make_ohlcv(n=10)
    df.loc[df.index[-1], "timestamp"] = _utc_now_ms() - TIMEFRAME_MS["1h"] * 10
    layer = DataLayer()
    with pytest.raises(StaleDataError):
        layer._validate_freshness(df, "1h")


def test_mid_price_from_ticker():
    layer = DataLayer()

    class FakeSpot:
        def fetch_ticker(self, symbol):
            return {"bid": 100.0, "ask": 102.0}

    layer.spot = FakeSpot()
    assert layer.get_mid_price("BTC/USDT") == 101.0


def test_mid_price_fallback_last():
    layer = DataLayer()

    class FakeSpot:
        def fetch_ticker(self, symbol):
            return {"last": 99.5}

    layer.spot = FakeSpot()
    assert layer.get_mid_price("ETH/USDT") == 99.5
