from engine.lanes.structure import analyze_structure
from tests.conftest import make_ohlcv


def test_structure_returns_lane_result():
    df = make_ohlcv()
    book = {
        "bids": [[df["close"].iloc[-1] * 0.999, 10.0]] * 50,
        "asks": [[df["close"].iloc[-1] * 1.001, 10.0]] * 50,
    }
    result = analyze_structure(df, book, "BTC/USDT")
    assert result.name == "structure"
    assert -100 <= result.score <= 100
    assert len(result.evidence) > 0


def test_no_edge_mid_range():
    df = make_ohlcv(n=500, trend=0.0, noise=0.0005)
    result = analyze_structure(df, None, "BTC/USDT")
    assert isinstance(result.no_edge, bool)


def test_ask_wall_resistance():
    df = make_ohlcv(n=500, trend=0.0, noise=0.0005, start=150.0)
    price = float(df["close"].iloc[-1])
    ask_price = price * 1.001
    book = {
        "bids": [[price * 0.99, 1.0]] * 100,
        "asks": [[ask_price, 3000.0]] + [[price * 1.05, 1.0]] * 99,
    }
    result = analyze_structure(df, book, "SOL/USDT")
    assert any("ask wall" in e.lower() for e in result.evidence)
