"""Internal research dashboard API (Phase 10 — backend only)."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from research_platform.config import get_research_settings
from research_platform.repository.registry import get_research_repository

router = APIRouter(prefix="/internal/research/v1", tags=["internal-research"])


def _require_internal() -> None:
    settings = get_research_settings()
    if not settings.research_internal_api_enabled:
        raise HTTPException(status_code=404, detail="Not found")


@router.get("/summary")
def research_summary() -> dict:
    _require_internal()
    repo = get_research_repository()
    return {
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "database": repo.health(),
    }


@router.get("/datasets")
def list_datasets(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return {"items": [], "enabled": False}
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import DatasetVersion

    with research_session() as session:
        if session is None:
            return {"items": []}
        rows = session.scalars(select(DatasetVersion).limit(limit)).all()
    return {
        "items": [
            {
                "version_code": r.version_code,
                "status": r.status,
                "dataset_hash": r.dataset_hash,
                "frozen_at": r.frozen_at.isoformat() if r.frozen_at else None,
            }
            for r in rows
        ]
    }


@router.get("/experiments")
def list_experiments(limit: int = 30) -> dict:
    _require_internal()
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return {"runs": []}
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import ExperimentRun

    with research_session() as session:
        if session is None:
            return {"runs": []}
        rows = session.scalars(select(ExperimentRun).order_by(ExperimentRun.created_at.desc()).limit(limit)).all()
    return {
        "runs": [
            {
                "id": r.id,
                "variant": r.variant,
                "run_kind": r.run_kind,
                "status": r.status,
                "config_hash": r.config_hash,
                "dataset_version_id": r.dataset_version_id,
                "metrics": r.metrics,
            }
            for r in rows
        ]
    }


@router.get("/promotions")
def list_promotions(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return {"records": []}
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import PromotionRecord

    with research_session() as session:
        if session is None:
            return {"records": []}
        rows = session.scalars(select(PromotionRecord).order_by(PromotionRecord.approved_at.desc()).limit(limit)).all()
    return {
        "records": [
            {
                "feature_name": r.feature_name,
                "decision": r.decision,
                "promotion_class": r.promotion_class,
                "approved_at": r.approved_at.isoformat(),
                "metrics_delta": r.metrics_delta,
            }
            for r in rows
        ]
    }


@router.get("/quality")
def quality_rollup(limit: int = 20) -> dict:
    _require_internal()
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return {"reports": []}
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.quality import DataQualityReport

    with research_session() as session:
        if session is None:
            return {"reports": []}
        rows = session.scalars(select(DataQualityReport).order_by(DataQualityReport.run_at.desc()).limit(limit)).all()
    return {
        "reports": [
            {
                "id": r.id,
                "symbol": r.symbol,
                "series": r.series,
                "severity": r.severity,
                "missing_bars": r.missing_bars,
                "duplicate_bars": r.duplicate_bars,
                "run_at": r.run_at.isoformat(),
            }
            for r in rows
        ]
    }


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
    from pathlib import Path

    roots = [Path("data/mds"), Path("data/datasets"), Path("research/artifacts")]
    usage = {}
    for root in roots:
        if not root.exists():
            usage[str(root)] = 0
            continue
        total = sum(f.stat().st_size for f in root.rglob("*") if f.is_file())
        usage[str(root)] = total
    return {"bytes_by_path": usage, "note": "Local filesystem estimate only"}
