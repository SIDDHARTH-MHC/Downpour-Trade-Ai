from engine.explanation import build_explanation
from engine.models import LaneResult, RegimeResult, Verdict
from engine.synthesizer import synthesize
from engine.config import load_config


def _regime():
    cfg = load_config()
    return RegimeResult(
        regime="RANGING",
        tradeable=True,
        lane_weights=cfg.regime.weights["RANGING"],
    )


def test_explanation_generated():
    lanes = [
        LaneResult("technical", 45, ["RSI(14)=41.3 recovering (+10)"], {}),
        LaneResult("flow", 40, ["OI +6.2% with price +1.8% (+15)"], {}),
        LaneResult("structure", 35, ["bid wall $9.5M at 65431 (+20)"], {}),
    ]
    verdict = synthesize(lanes, _regime())
    assert verdict.explanation is not None
    assert verdict.explanation.decision == verdict.action
    assert len(verdict.explanation.why) + len(verdict.explanation.why_not) > 0


def test_explanation_no_trade():
    lanes = [
        LaneResult("technical", 10, ["neutral (0)"], {}),
        LaneResult("flow", 5, ["neutral (0)"], {}),
        LaneResult("structure", 0, ["mid-range no_edge"], {}, no_edge=True),
    ]
    verdict = synthesize(lanes, _regime())
    exp = build_explanation(verdict)
    assert exp.decision == "NO_TRADE"
    assert len(exp.why_not) > 0
