"""Build deterministic replay timeline from a verdict payload."""

from __future__ import annotations

from typing import Any


def build_replay_events(payload: dict[str, Any]) -> list[dict[str, str]]:
    events: list[dict[str, str]] = []
    order = 0

    def add(category: str, label: str) -> None:
        nonlocal order
        order += 1
        events.append({"step": str(order), "category": category, "label": label})

    regime = payload.get("regime") or {}
    for line in regime.get("evidence") or []:
        add("regime", line)

    for lane in payload.get("lanes") or []:
        name = lane.get("name", "lane")
        for line in (lane.get("evidence") or [])[:6]:
            add(name, line)

    for ev in payload.get("structure_events") or []:
        add("structure", ev.get("label") or str(ev))

    for reason in payload.get("reasons") or []:
        add("synthesizer", reason)

    exp = payload.get("explanation") or {}
    for line in (exp.get("why") or [])[:4]:
        add("decision", line)
    for line in (exp.get("why_not") or [])[:3]:
        add("decision", f"(caution) {line}")

    plan = payload.get("trade_plan")
    if plan:
        add(
            "trade_plan",
            f"Plan: entry {plan.get('entry')} · SL {plan.get('stop_loss')} · TP1 {plan.get('tp1')}",
        )

    action = payload.get("action", "NO_TRADE")
    add("verdict", f"Verdict: {action} · score {payload.get('weighted_score')}")

    return events
