from engine.attribution import compute_attribution
from engine.models import LaneResult, RegimeResult


def test_attribution_sums_to_one():
    regime = RegimeResult(
        regime="RANGING",
        tradeable=True,
        lane_weights={"technical": 1.0, "flow": 1.0, "structure": 1.0},
    )
    lanes = [
        LaneResult("technical", 40, [], {}),
        LaneResult("flow", 20, [], {}),
        LaneResult("structure", 10, [], {}),
    ]
    attr = compute_attribution(lanes, regime)
    assert abs(sum(attr.values()) - 1.0) < 1e-6
    assert attr["technical"] > attr["flow"] > attr["structure"]
