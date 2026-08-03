"""Signal lifecycle stage from stored verdict + outcome."""

from __future__ import annotations

from typing import Any

STAGES = [
    "detected",
    "waiting",
    "confirmed",
    "entry_hit",
    "tp1",
    "tp2",
    "closed",
]


def lifecycle_state(payload: dict[str, Any], outcome: str | None) -> dict[str, Any]:
    action = payload.get("action", "NO_TRADE")
    if action not in {"LONG", "SHORT"}:
        return {"stage": "none", "label": "Not a trade signal", "steps": []}

    plan = payload.get("trade_plan")
    patient = bool(plan.get("patient")) if plan else False

    if outcome == "TP1":
        current = "tp1"
    elif outcome == "TP2":
        current = "tp2"
    elif outcome in {"SL", "LOSS"}:
        current = "closed"
    elif outcome == "TIMEOUT":
        current = "closed"
    elif outcome is None:
        if not plan:
            current = "detected"
        elif patient:
            current = "waiting"
        else:
            current = "confirmed"
    else:
        current = "closed"

    labels = {
        "detected": "Detected",
        "waiting": "Waiting (patient entry)",
        "confirmed": "Confirmed",
        "entry_hit": "Entry hit",
        "tp1": "TP1 reached",
        "tp2": "TP2 reached",
        "closed": "Closed",
    }

    steps = []
    for key in STAGES:
        if key == "tp2" and outcome != "TP2":
            continue
        if key == "entry_hit" and current in {"detected", "waiting", "confirmed"} and outcome is None:
            status = "upcoming"
        elif _stage_index(key) < _stage_index(current):
            status = "done"
        elif key == current or (key == "closed" and current == "closed"):
            status = "current"
        elif _stage_index(key) > _stage_index(current):
            status = "upcoming"
        else:
            status = "upcoming"
        steps.append({"id": key, "label": labels[key], "status": status})

    return {"stage": current, "label": labels.get(current, current), "steps": steps, "outcome": outcome}


def _stage_index(stage: str) -> int:
    order = ["detected", "waiting", "confirmed", "entry_hit", "tp1", "tp2", "closed"]
    try:
        return order.index(stage)
    except ValueError:
        return 0
