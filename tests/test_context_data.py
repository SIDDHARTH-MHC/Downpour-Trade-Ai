from engine.backtest import _long_short_as_of
from engine.context_data import fetch_liquidations_context


def test_long_short_as_of_trims_future_bars():
    history = [
        {"timestamp": 1000, "longShortRatio": "1.1"},
        {"timestamp": 2000, "longShortRatio": "1.2"},
        {"timestamp": 3000, "longShortRatio": "1.3"},
    ]
    assert len(_long_short_as_of(history, 2000)) == 2
    assert _long_short_as_of(history, 2000)[-1]["longShortRatio"] == "1.2"


def test_liquidations_context_reference_when_stress_errors(monkeypatch):
    def _fail(_symbol: str, period: str = "1h", limit: int = 48):
        return {"symbol": "BTC/USDT", "error": "offline"}

    monkeypatch.setattr("engine.context_data.fetch_taker_stress", _fail)
    payload = fetch_liquidations_context("BTC/USDT")
    assert payload["status"] == "reference_only"
    assert payload["stress"]["error"] == "offline"
