"""Combine lanes into a verdict."""

from __future__ import annotations

from engine.config import EngineConfig, load_config
from engine.models import LaneResult, RegimeResult, Verdict


def _lane_conflict(lanes: list[LaneResult], threshold: float) -> bool:
    scores = [lane.score for lane in lanes if lane.name in {"technical", "flow", "structure"}]
    if len(scores) < 2:
        return False
    return max(scores) - min(scores) > threshold


def synthesize(
    lanes: list[LaneResult],
    regime: RegimeResult,
    config: EngineConfig | None = None,
) -> Verdict:
    cfg = (config or load_config()).synthesizer
    scored_lanes = [lane for lane in lanes if lane.name in {"technical", "flow", "structure"}]

    if not regime.tradeable or regime.regime == "SHOCK":
        return Verdict(
            action="NO_TRADE",
            weighted_score=0.0,
            lanes=lanes,
            regime=regime,
            confidence="N/A — regime not tradeable",
            trade_plan=None,
            reasons=[f"regime={regime.regime} → forced NO-TRADE"],
        )

    weighted_sum = 0.0
    weight_total = 0.0
    for lane in scored_lanes:
        w = regime.lane_weights.get(lane.name, 1.0)
        weighted_sum += lane.score * w
        weight_total += w

    weighted_score = weighted_sum / weight_total if weight_total else 0.0
    reasons: list[str] = []

    structure_lane = next((lane for lane in lanes if lane.name == "structure"), None)
    no_edge = structure_lane.no_edge if structure_lane else False

    bullish_aligned = sum(1 for lane in scored_lanes if lane.score >= cfg.lane_alignment_threshold)
    bearish_aligned = sum(1 for lane in scored_lanes if lane.score <= -cfg.lane_alignment_threshold)
    adverse_long = any(lane.score <= cfg.max_adverse_lane for lane in scored_lanes)
    adverse_short = any(lane.score >= cfg.min_adverse_lane_short for lane in scored_lanes)

    action = "NO_TRADE"

    if _lane_conflict(scored_lanes, cfg.lane_conflict_threshold):
        reasons.append(
            f"lane conflict: spread {max(l.score for l in scored_lanes) - min(l.score for l in scored_lanes):.1f} > {cfg.lane_conflict_threshold:.0f}"
        )
    elif (
        weighted_score >= cfg.long_threshold
        and bullish_aligned >= cfg.min_aligned_lanes
        and not adverse_long
        and not no_edge
    ):
        action = "LONG"
        reasons.append(f"weighted score {weighted_score:.1f} ≥ +{cfg.long_threshold:.0f}")
        reasons.append(f"lanes aligned {bullish_aligned}/{len(scored_lanes)} beyond +{cfg.lane_alignment_threshold:.0f}")
    elif (
        weighted_score <= cfg.short_threshold
        and bearish_aligned >= cfg.min_aligned_lanes
        and not adverse_short
        and not no_edge
    ):
        action = "SHORT"
        reasons.append(f"weighted score {weighted_score:.1f} ≤ {cfg.short_threshold:.0f}")
        reasons.append(f"lanes aligned {bearish_aligned}/{len(scored_lanes)} beyond -{cfg.lane_alignment_threshold:.0f}")
    else:
        if abs(weighted_score) < cfg.long_threshold:
            reasons.append(
                f"weighted score {weighted_score:.1f} within neutral band (needs ≥ +{cfg.long_threshold:.0f} for LONG or ≤ {cfg.short_threshold:.0f} for SHORT)"
            )
        if bullish_aligned < cfg.min_aligned_lanes and bearish_aligned < cfg.min_aligned_lanes:
            reasons.append(
                f"lanes not aligned ({max(bullish_aligned, bearish_aligned)}/{len(scored_lanes)} beyond ±{cfg.lane_alignment_threshold:.0f})"
            )
        if no_edge:
            reasons.append("structure lane flagged no_edge=True")
        if adverse_long or adverse_short:
            reasons.append("adverse lane score present")

    return Verdict(
        action=action,
        weighted_score=weighted_score,
        lanes=lanes,
        regime=regime,
        confidence="pending calibration",
        trade_plan=None,
        reasons=reasons,
    )
