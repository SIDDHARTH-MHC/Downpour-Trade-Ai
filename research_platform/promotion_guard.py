"""Promotion gate: configuration promotion is always manual (never scheduled)."""

from __future__ import annotations

MANUAL_PROMOTION_ONLY = True


def assert_manual_promotion_only(*, context: str) -> None:
    if not MANUAL_PROMOTION_ONLY:
        raise RuntimeError("Manual promotion gate disabled — forbidden")
    if context.lower().startswith("auto") or "scheduled" in context.lower():
        raise RuntimeError(
            f"Automatic promotion blocked ({context}). "
            "Promotion requires human approval per Research_Roadmap.md."
        )


def validate_promotion_decision(decision: str, *, source: str) -> None:
    """Call before writing promotion_records from application code."""
    assert_manual_promotion_only(context=source)
    allowed = {"PROMOTED", "REJECTED", "DEFERRED", "DRAFT"}
    if decision.upper() not in allowed:
        raise ValueError(f"Invalid promotion decision: {decision}")
    if source == "scheduler":
        raise RuntimeError("Scheduler cannot record PROMOTED/REJECTED decisions")
