from engine.config import load_config
from engine.config_hash import config_hash
from engine.lanes.technical import analyze_technical
from research.variants import config_for_variant
from tests.conftest import make_ohlcv


def test_config_hash_stable():
    cfg = load_config()
    assert config_hash(cfg) == config_hash(cfg)
    assert len(config_hash(cfg)) == 16


def test_r0_b0_differs_from_t3_hash():
    b0 = config_for_variant("B0")
    t3 = config_for_variant("T3")
    assert config_hash(b0) != config_hash(t3)


def test_ema200_skipped_when_stack_bullish():
    df = make_ohlcv(n=500, trend=0.01, noise=0.0)
    cfg = config_for_variant("T3")
    result = analyze_technical(df, df, config=cfg)
    assert any("EMA200 side skipped" in ev for ev in result.evidence)


def test_b0_still_applies_ema200_with_stack():
    df = make_ohlcv(n=500, trend=0.01, noise=0.0)
    cfg = config_for_variant("B0")
    result = analyze_technical(df, df, config=cfg)
    assert not any("EMA200 side skipped" in ev for ev in result.evidence)
    assert any("EMA200" in ev for ev in result.evidence)


def test_t3_score_differs_from_b0_on_trending_series():
    df = make_ohlcv(n=500, trend=0.01, noise=0.0)
    b0 = analyze_technical(df, df, config=config_for_variant("B0"))
    t3 = analyze_technical(df, df, config=config_for_variant("T3"))
    assert b0.score != t3.score
