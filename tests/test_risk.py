from engine.config import load_config
from engine.models import LaneResult, RegimeResult, Verdict
from engine.risk import build_trade_plan
from tests.conftest import make_ohlcv


def _verdict(action: str) -> Verdict:
    return Verdict(
        action=action,
        weighted_score=40 if action == "LONG" else -40,
        lanes=[
            LaneResult("structure", 20, [], {"nearest_support": 95.0, "nearest_resistance": 110.0}),
            LaneResult("technical", 30, [], {}),
            LaneResult("flow", 25, [], {}),
        ],
        regime=RegimeResult("RANGING", True, {"technical": 1.0, "flow": 1.0, "structure": 1.0}),
        confidence="test",
        trade_plan=None,
        reasons=[],
    )


def test_long_trade_plan():
    df = make_ohlcv(start=100.0)
    verdict = build_trade_plan(_verdict("LONG"), df, mid_price=100.5, config=load_config())
    assert verdict.trade_plan is not None
    assert verdict.trade_plan.entry > 0
    assert verdict.trade_plan.stop_loss < verdict.trade_plan.entry
    assert verdict.trade_plan.reward_risk >= 1.2


def test_poor_rr_downgrades():
    df = make_ohlcv(start=100.0)
    v = _verdict("LONG")
    v.lanes[0].values["nearest_resistance"] = df["close"].iloc[-1] + 0.01
    verdict = build_trade_plan(v, df, config=load_config())
    assert verdict.action == "NO_TRADE"


def test_no_trade_unchanged():
    df = make_ohlcv()
    v = _verdict("NO_TRADE")
    v.action = "NO_TRADE"
    verdict = build_trade_plan(v, df, config=load_config())
    assert verdict.trade_plan is None
