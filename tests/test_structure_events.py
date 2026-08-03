from tests.conftest import make_ohlcv
from engine.structure_events import detect_structure_events


def test_structure_events_runs_on_sample():
    df = make_ohlcv(120)
    events = detect_structure_events(df, fractal=3)
    assert isinstance(events, list)
