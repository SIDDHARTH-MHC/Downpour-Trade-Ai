import pandas as pd

from engine.indicators import session_vwap


def test_session_vwap_weighted():
    df = pd.DataFrame(
        {
            "high": [10.0, 12.0],
            "low": [8.0, 10.0],
            "close": [9.0, 11.0],
            "volume": [100.0, 300.0],
            "timestamp": [1_700_000_000_000, 1_700_000_360_000],
        }
    )
    v = session_vwap(df)
    assert 10.0 < v < 11.5
