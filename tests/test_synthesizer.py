from engine.config import load_config
from engine.lanes.regime import analyze_regime
from engine.lanes.technical import analyze_technical
from engine.models import LaneResult, RegimeResult
from engine.synthesizer import synthesize
from tests.conftest import make_ohlcv


def _regime(tradeable=True, regime="RANGING"):
    cfg = load_config()
    return RegimeResult(
        regime=regime,
        tradeable=tradeable,
        lane_weights=cfg.regime.weights.get(regime, {"technical": 1.0, "flow": 1.0, "structure": 1.0}),
    )


def test_no_trade_default():
    lanes = [
        LaneResult("technical", 10, ["neutral"], {}),
        LaneResult("flow", 5, ["neutral"], {}),
        LaneResult("structure", 0, ["mid"], {}, no_edge=True),
    ]
    verdict = synthesize(lanes, _regime())
    assert verdict.action == "NO_TRADE"


def test_long_when_aligned():
    lanes = [
        LaneResult("technical", 45, ["bull"], {}),
        LaneResult("flow", 40, ["bull"], {}),
        LaneResult("structure", 35, ["support"], {}),
    ]
    verdict = synthesize(lanes, _regime(regime="TRENDING_UP"))
    assert verdict.action == "LONG"


def test_conflict_forces_no_trade():
    lanes = [
        LaneResult("technical", 45, ["bull"], {}),
        LaneResult("flow", -40, ["bear"], {}),
        LaneResult("structure", 10, ["mixed"], {}),
    ]
    verdict = synthesize(lanes, _regime())
    assert verdict.action == "NO_TRADE"


def test_shock_regime_blocks():
    lanes = [
        LaneResult("technical", 50, ["bull"], {}),
        LaneResult("flow", 50, ["bull"], {}),
        LaneResult("structure", 50, ["bull"], {}),
    ]
    verdict = synthesize(lanes, _regime(tradeable=False, regime="SHOCK"))
    assert verdict.action == "NO_TRADE"
