"""Internal research dashboard API (Phase 10 — backend only)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from research_platform.config import get_research_settings
from research_platform.repository.registry import get_research_repository

router = APIRouter(prefix="/internal/research/v1", tags=["internal-research"])


def _require_internal() -> None:
    settings = get_research_settings()
    if not settings.research_internal_api_enabled:
        raise HTTPException(status_code=404, detail="Not found")


class PromotionDecisionBody(BaseModel):
    decision: Literal["PROMOTED", "REJECTED", "DEFERRED"]
    reason: str = Field(min_length=1, max_length=4000)
    approved_by: str = Field(min_length=1, max_length=128)
    promotion_class: str = Field(default="P2", max_length=8)
    feature_name: Optional[str] = Field(default=None, max_length=128)


@router.get("/dashboard")
def research_dashboard() -> dict:
    """Unified snapshot for the internal Research Ops UI."""
    _require_internal()
    from research_platform.dashboard.snapshot import build_dashboard_snapshot

    return build_dashboard_snapshot()


@router.get("/summary")
def research_summary() -> dict:
    _require_internal()
    from research_platform.jobs import research_automation_status

    repo = get_research_repository()
    return {
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "database": repo.health(),
        "automation": research_automation_status(),
    }


@router.post("/promotion-queue/{run_id}/decide")
def promotion_decide(run_id: str, body: PromotionDecisionBody) -> dict:
    _require_internal()
    from research_platform.promotion_service import decide_experiment_run

    try:
        return decide_experiment_run(
            run_id,
            body.decision,
            reason=body.reason,
            approved_by=body.approved_by,
            promotion_class=body.promotion_class,
            feature_name=body.feature_name,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/datasets")
def list_datasets(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.dashboard.snapshot import list_dataset_versions

    items = list_dataset_versions(limit=limit)
    return {"items": items, "enabled": get_research_settings().research_db_enabled}


@router.get("/experiments")
def list_experiments(limit: int = 30) -> dict:
    _require_internal()
    from research_platform.dashboard.snapshot import experiment_history

    return {"runs": experiment_history(limit=limit)}


@router.get("/promotions")
def list_promotions(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.dashboard.snapshot import promotion_history

    return {"records": promotion_history(limit=limit)}


@router.get("/promotion-queue")
def list_promotion_queue(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.dashboard.snapshot import promotion_queue

    return {"items": promotion_queue(limit=limit), "policy": "manual_only"}


@router.get("/quality")
def quality_rollup(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.dashboard.snapshot import quality_health

    return quality_health(limit=limit)


@router.get("/queue")
def research_queue(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return {"jobs": []}
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.platform_extras import ResearchJob

    with research_session() as session:
        if session is None:
            return {"jobs": []}
        rows = session.scalars(select(ResearchJob).order_by(ResearchJob.created_at.desc()).limit(limit)).all()
    return {
        "jobs": [
            {
                "id": j.id,
                "job_kind": j.job_kind,
                "status": j.status,
                "progress": j.progress,
                "created_at": j.created_at.isoformat(),
            }
            for j in rows
        ]
    }


@router.get("/storage")
def storage_usage() -> dict:
    _require_internal()
    from research_platform.dashboard.snapshot import filesystem_storage, timescale_storage

    return {
        "filesystem": filesystem_storage(),
        "timescale": timescale_storage(),
    }


@router.get("/logs")
def research_logs(limit: int = 50) -> dict:
    _require_internal()
    from research_platform.dashboard.snapshot import research_activity_log

    return {"entries": research_activity_log(limit=limit)}
