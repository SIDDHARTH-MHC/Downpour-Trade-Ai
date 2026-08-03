"""Manual promotion decisions from the internal dashboard (never scheduler)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from research_platform.promotion_guard import validate_promotion_decision


def decide_experiment_run(
    run_id: str,
    decision: str,
    *,
    reason: str,
    approved_by: str,
    promotion_class: str = "P2",
    feature_name: str | None = None,
) -> dict[str, Any]:
    validate_promotion_decision(decision, source="manual_dashboard")
    if not reason.strip():
        raise ValueError("decision_reason is required")
    if not approved_by.strip():
        raise ValueError("approved_by is required")

    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import ExperimentRun, PromotionRecord

    decision_up = decision.upper()
    with research_session() as session:
        if session is None:
            raise RuntimeError("Research database unavailable")
        run = session.get(ExperimentRun, run_id)
        if run is None:
            raise LookupError(f"Experiment run not found: {run_id}")
        if run.status != "completed":
            raise ValueError("Only completed runs can be decided")

        run.promotion_decision = decision_up
        if decision_up == "REJECTED":
            run.rejection_reason = reason
        elif decision_up == "PROMOTED":
            run.acceptance_reason = reason

        fname = feature_name or f"run:{run.variant}:{run.id[:8]}"
        record = PromotionRecord(
            id=str(uuid.uuid4()),
            engine_release_id=None,
            experiment_run_id=run.id,
            dataset_version_id=run.dataset_version_id,
            feature_name=fname,
            roadmap_id=None,
            promotion_class=promotion_class,
            decision=decision_up,
            decision_reason=reason,
            baseline_variant="B0",
            metrics_delta=run.metrics if isinstance(run.metrics, dict) else {},
            integration_scope=None,
            rollback_plan=None,
            approved_by=approved_by.strip(),
            approved_at=datetime.now(timezone.utc),
            prior_config_hash=None,
            new_config_hash=run.config_hash,
        )
        session.add(record)
        session.flush()
        record_id = record.id

    return {
        "run_id": run_id,
        "decision": decision_up,
        "promotion_record_id": record_id,
        "note": "Recorded only — engine config is not auto-deployed.",
    }
