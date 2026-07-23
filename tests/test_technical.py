from engine.lanes.technical import analyze_technical
from tests.conftest import make_chop_ohlcv, make_ohlcv


def test_monotonic_up_scores_bullish():
    df = make_ohlcv(n=500, trend=0.01, noise=0.0)
    result = analyze_technical(df, df)
    assert result.score >= 50
    assert all(any(c.isdigit() for c in ev) for ev in result.evidence)


def test_chop_scores_low():
    df = make_chop_ohlcv(n=500)
    result = analyze_technical(df, df)
    assert abs(result.score) <= 15


def test_deterministic():
    df = make_ohlcv()
    a = analyze_technical(df, df)
    b = analyze_technical(df, df)
    assert a.score == b.score
    assert a.evidence == b.evidence
