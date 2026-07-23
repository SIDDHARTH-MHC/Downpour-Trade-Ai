import numpy as np

from engine.lanes.flow import _funding_zscore
from engine.config import load_config


def test_funding_zscore_extreme_short():
    cfg = load_config().flow
    history = [{"fundingRate": 0.0005} for _ in range(30)]
    current = -0.002
    score, ev = _funding_zscore(history, current, cfg)
    assert score == cfg.funding_zscore_bull
    assert "z=" in ev


def test_funding_zscore_unavailable():
    cfg = load_config().flow
    score, ev = _funding_zscore([], None, cfg)
    assert score == 0.0
    assert "unavailable" in ev
