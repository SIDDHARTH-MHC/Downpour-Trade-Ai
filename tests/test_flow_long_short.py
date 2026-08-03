from engine.config import load_config
from engine.lanes.flow import _long_short_zscore


def test_long_short_zscore_extreme_short_crowd():
    cfg = load_config().flow
    history = [{"longShortRatio": 1.0 + i * 0.01} for i in range(15)]
    history.append({"longShortRatio": 2.5})
    score, ev = _long_short_zscore(history, cfg)
    assert score == cfg.long_short_zscore_bear
    assert "z=" in ev


def test_long_short_insufficient_data():
    cfg = load_config().flow
    score, ev = _long_short_zscore([{"longShortRatio": 1.1}], cfg)
    assert score == 0.0
