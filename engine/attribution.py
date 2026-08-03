"""Lane contribution to weighted score (display-only)."""

from __future__ import annotations

from engine.models import LaneResult, RegimeResult

SCORED_LANES = ("technical", "flow", "structure")


def compute_attribution(lanes: list[LaneResult], regime: RegimeResult) -> dict[str, float]:
    """Normalized share of weighted sum per lane (sums to 1.0 when tradeable)."""
    weights = regime.lane_weights or {}
    parts: dict[str, float] = {}
    total = 0.0
    for lane in lanes:
        if lane.name not in SCORED_LANES:
            continue
        w = weights.get(lane.name, 1.0)
        contrib = abs(lane.score) * w
        parts[lane.name] = contrib
        total += contrib
    if total <= 0:
        equal = 1.0 / len(SCORED_LANES)
        return {name: equal for name in SCORED_LANES}
    return {name: parts.get(name, 0.0) / total for name in SCORED_LANES}
