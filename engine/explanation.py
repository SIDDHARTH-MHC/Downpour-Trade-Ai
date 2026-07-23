"""Structured explanation block — formatting layer over lane evidence (§12)."""

from __future__ import annotations

from engine.models import Explanation, Verdict


def build_explanation(verdict: Verdict) -> Explanation:
    action = verdict.action
    why: list[str] = []
    why_not: list[str] = []

    for lane in verdict.lanes:
        for line in lane.evidence:
            if action == "NO_TRADE":
                if lane.score >= 20:
                    why.append(line)
                elif lane.score <= -20:
                    why_not.append(line)
                elif "no_edge" in line.lower() or "mid-range" in line.lower():
                    why_not.append(line)
                else:
                    why_not.append(line)
            elif action == "LONG":
                if lane.score >= 10 and ("+" in line or "bull" in line.lower() or "support" in line.lower()):
                    why.append(line)
                elif lane.score <= -10 or "(-" in line or "resist" in line.lower() or "ask wall" in line.lower():
                    why_not.append(line)
            elif action == "SHORT":
                if lane.score <= -10 and ("(-" in line or "bear" in line.lower() or "resist" in line.lower()):
                    why.append(line)
                elif lane.score >= 10 or "support" in line.lower() or "bid wall" in line.lower():
                    why_not.append(line)

    for reason in verdict.reasons:
        if action == "NO_TRADE":
            why_not.append(reason)
        elif "downgraded" in reason.lower() or "conflict" in reason.lower():
            why_not.append(reason)
        else:
            why.append(reason)

    for line in verdict.regime.evidence:
        if not verdict.regime.tradeable or "NO-TRADE" in line:
            why_not.append(line)
        else:
            why.append(line)

    risk: list[str] = []
    if verdict.trade_plan:
        tp = verdict.trade_plan
        risk.append(
            f"Entry {tp.entry:.2f} · SL {tp.stop_loss:.2f} · TP1 {tp.tp1:.2f} · TP2 {tp.tp2:.2f}"
        )
        risk.append(
            f"R:R to TP1 = {tp.reward_risk:.2f} · size {tp.size_coin:.6f} (${tp.size_usd:.2f}) at 1% risk"
        )
    if verdict.confidence and verdict.confidence not in {"pending calibration", "N/A"}:
        risk.append(f"Confidence: {verdict.confidence}")

    return Explanation(
        decision=action,
        why=why[:12],
        why_not=why_not[:12],
        risk=risk,
    )
