from engine.lanes.flow import analyze_flow
from tests.conftest import make_ohlcv


def test_funding_short_crowd_bullish():
    df = make_ohlcv()
    funding = {
        "current": {"fundingRate": -0.0002},
        "history": [{"fundingRate": -0.0001}] * 8,
    }
    result = analyze_flow(df, funding, df.iloc[:0], trades=[])
    assert result.score > 0
    assert any("funding" in e.lower() for e in result.evidence)


def test_neutral_funding():
    df = make_ohlcv()
    funding = {"current": {"fundingRate": 0.0}, "history": [{"fundingRate": 0.0}] * 8}
    result = analyze_flow(df, funding, df.iloc[:0], trades=[])
    assert any("neutral" in e.lower() for e in result.evidence)
