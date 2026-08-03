"""Aggregate data for the internal research dashboard API."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api.db import Database
from api.scheduler import calibration_status, scheduler_jobs_snapshot


def _utcnow_label() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _parse_meta_json(raw: str) -> dict[str, Any] | None:
    if not raw or raw.startswith("skipped"):
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def filesystem_storage() -> dict[str, Any]:
    roots = [Path("data/mds"), Path("data/datasets"), Path("research/artifacts")]
    usage: dict[str, int] = {}
    for root in roots:
        if not root.exists():
            usage[str(root)] = 0
            continue
        usage[str(root)] = sum(f.stat().st_size for f in root.rglob("*") if f.is_file())
    return {"bytes_by_path": usage, "total_bytes": sum(usage.values())}


def timescale_storage() -> dict[str, Any]:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return {"enabled": False}
    from sqlalchemy import text

    from research_platform.db.session import research_session

    with research_session() as session:
        if session is None:
            return {"enabled": True, "connected": False}
        try:
            db_bytes = session.execute(text("SELECT pg_database_size(current_database())")).scalar()
            rows = session.execute(
                text(
                    """
                    SELECT hypertable_schema || '.' || hypertable_name AS name,
                           hypertable_size(
                               format('%I.%I', hypertable_schema, hypertable_name)::regclass
                           ) AS size_bytes
                    FROM timescaledb_information.hypertables
                    ORDER BY size_bytes DESC
                    """
                )
            ).all()
            tables = [{"name": r[0], "bytes": int(r[1] or 0)} for r in rows]
        except Exception as exc:  # noqa: BLE001
            try:
                db_bytes = session.execute(text("SELECT pg_database_size(current_database())")).scalar()
                tables = []
            except Exception as inner:  # noqa: BLE001
                return {"enabled": True, "connected": False, "error": str(inner)}
            return {
                "enabled": True,
                "connected": True,
                "database_bytes": int(db_bytes or 0),
                "hypertables": tables,
                "note": f"Hypertable stats unavailable: {exc}",
            }
        return {
            "enabled": True,
            "connected": True,
            "database_bytes": int(db_bytes or 0),
            "hypertables": tables,
        }


def collector_progress() -> dict[str, Any]:
    from research_platform.config import get_research_settings
    from research_platform.jobs import research_automation_status

    auto = research_automation_status()
    last = _parse_meta_json(auto.get("collector_last", "") or "")
    watermarks: list[dict[str, Any]] = []
    if get_research_settings().research_db_enabled:
        from sqlalchemy import select

        from research_platform.db.session import research_session
        from research_platform.models.dimensions import IngestWatermark

        with research_session() as session:
            if session is not None:
                rows = session.scalars(select(IngestWatermark).limit(50)).all()
                watermarks = [
                    {
                        "symbol": w.symbol,
                        "series": w.series,
                        "exchange_id": w.exchange_id,
                        "last_ts": w.last_ts.isoformat() if w.last_ts else None,
                        "updated_at": w.updated_at.isoformat(),
                    }
                    for w in rows
                ]
    return {"last_run": last, "watermarks": watermarks}


def quality_health(limit: int = 15) -> dict[str, Any]:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return {"enabled": False, "reports": [], "summary": {"ok": 0, "warning": 0, "critical": 0}}
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.quality import DataQualityReport

    with research_session() as session:
        if session is None:
            return {"enabled": True, "reports": [], "summary": {"ok": 0, "warning": 0, "critical": 0}}
        rows = session.scalars(select(DataQualityReport).order_by(DataQualityReport.run_at.desc()).limit(limit)).all()
    summary = {"ok": 0, "warning": 0, "critical": 0}
    for r in rows:
        sev = (r.severity or "ok").lower()
        if sev in summary:
            summary[sev] += 1
        elif sev == "error":
            summary["critical"] += 1
    return {
        "enabled": True,
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
        ],
        "summary": summary,
    }


def list_dataset_versions(limit: int = 20) -> list[dict[str, Any]]:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return []
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import DatasetVersion

    with research_session() as session:
        if session is None:
            return []
        rows = session.scalars(select(DatasetVersion).order_by(DatasetVersion.created_at.desc()).limit(limit)).all()
    return [
        {
            "id": r.id,
            "version_code": r.version_code,
            "title": r.title,
            "status": r.status,
            "dataset_hash": r.dataset_hash,
            "symbols": list(r.symbols or []),
            "frozen_at": r.frozen_at.isoformat() if r.frozen_at else None,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


def latest_walk_forward_runs(limit: int = 10) -> list[dict[str, Any]]:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return []
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import ExperimentRun

    with research_session() as session:
        if session is None:
            return []
        rows = session.scalars(
            select(ExperimentRun)
            .where(ExperimentRun.run_kind.contains("walk_forward"))
            .order_by(ExperimentRun.created_at.desc())
            .limit(limit)
        ).all()
    return [_experiment_run_row(r) for r in rows]


def experiment_history(limit: int = 30) -> list[dict[str, Any]]:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return []
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import ExperimentRun

    with research_session() as session:
        if session is None:
            return []
        rows = session.scalars(select(ExperimentRun).order_by(ExperimentRun.created_at.desc()).limit(limit)).all()
    return [_experiment_run_row(r) for r in rows]


def _experiment_run_row(r) -> dict[str, Any]:
    return {
        "id": r.id,
        "variant": r.variant,
        "run_kind": r.run_kind,
        "status": r.status,
        "config_hash": r.config_hash,
        "symbols": list(r.symbols or []),
        "metrics": r.metrics,
        "promotion_decision": r.promotion_decision,
        "promotion_class": r.promotion_class,
        "created_at": r.created_at.isoformat(),
        "completed_at": r.completed_at.isoformat() if r.completed_at else None,
    }


def promotion_queue(limit: int = 20) -> list[dict[str, Any]]:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return []
    from sqlalchemy import or_, select

    from research_platform.db.session import research_session
    from research_platform.models.governance import ExperimentRun

    pending = or_(
        ExperimentRun.promotion_decision.is_(None),
        ExperimentRun.promotion_decision.in_(("", "PENDING", "DEFERRED")),
    )
    with research_session() as session:
        if session is None:
            return []
        rows = session.scalars(
            select(ExperimentRun)
            .where(ExperimentRun.status == "completed")
            .where(pending)
            .order_by(ExperimentRun.completed_at.desc().nullslast(), ExperimentRun.created_at.desc())
            .limit(limit)
        ).all()
    return [_experiment_run_row(r) for r in rows]


def promotion_history(limit: int = 20) -> list[dict[str, Any]]:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return []
    from sqlalchemy import select

    from research_platform.db.session import research_session
    from research_platform.models.governance import PromotionRecord

    with research_session() as session:
        if session is None:
            return []
        rows = session.scalars(select(PromotionRecord).order_by(PromotionRecord.approved_at.desc()).limit(limit)).all()
    return [
        {
            "id": r.id,
            "feature_name": r.feature_name,
            "decision": r.decision,
            "promotion_class": r.promotion_class,
            "approved_by": r.approved_by,
            "approved_at": r.approved_at.isoformat(),
            "decision_reason": r.decision_reason,
            "experiment_run_id": r.experiment_run_id,
        }
        for r in rows
    ]


def calibration_panel() -> dict[str, Any]:
    db = Database()
    status = calibration_status()
    stats = db.load_calibration()
    wf = stats.get("walk_forward") if isinstance(stats.get("walk_forward"), list) else []
    buckets = stats if isinstance(stats, dict) else {}
    bucket_keys = [k for k in buckets if k not in ("walk_forward",) and isinstance(buckets.get(k), dict)]
    return {
        **status,
        "walk_forward": wf,
        "bucket_labels": bucket_keys[:20],
        "bucket_count": len(bucket_keys),
    }


def research_activity_log(limit: int = 40) -> list[dict[str, Any]]:
    from research_platform.config import get_research_settings
    from research_platform.jobs import research_automation_status

    lines: list[dict[str, Any]] = []
    auto = research_automation_status()
    for key, label in (
        ("collector_last", "collector"),
        ("dq_last", "data_quality"),
        ("walk_forward_last", "walk_forward"),
    ):
        parsed = _parse_meta_json(str(auto.get(key, "") or ""))
        if parsed:
            lines.append(
                {
                    "kind": label,
                    "at": parsed.get("at") or parsed.get("raw", ""),
                    "status": parsed.get("status"),
                    "detail": parsed,
                }
            )

    if get_research_settings().research_db_enabled:
        from sqlalchemy import select

        from research_platform.db.session import research_session
        from research_platform.models.platform_extras import ResearchJob

        with research_session() as session:
            if session is not None:
                jobs = session.scalars(select(ResearchJob).order_by(ResearchJob.created_at.desc()).limit(limit)).all()
                for j in jobs:
                    lines.append(
                        {
                            "kind": j.job_kind,
                            "at": j.created_at.isoformat(),
                            "status": j.status,
                            "detail": {"progress": j.progress, "payload": j.payload},
                        }
                    )

    lines.sort(key=lambda x: str(x.get("at") or ""), reverse=True)
    return lines[:limit]


def build_dashboard_snapshot() -> dict[str, Any]:
    from research_platform.config import get_research_settings
    from research_platform.jobs import research_automation_status
    from research_platform.repository.registry import get_research_repository

    settings = get_research_settings()
    auto = research_automation_status()
    return {
        "data_as_of_utc": _utcnow_label(),
        "internal_api_enabled": settings.research_internal_api_enabled,
        "research_db_enabled": settings.research_db_enabled,
        "research_scheduler_enabled": settings.research_scheduler_enabled,
        "database": get_research_repository().health(),
        "scheduler": scheduler_jobs_snapshot(),
        "automation": auto,
        "collector": collector_progress(),
        "data_quality": quality_health(),
        "datasets": list_dataset_versions(),
        "storage": {
            "filesystem": filesystem_storage(),
            "timescale": timescale_storage(),
        },
        "walk_forward": {
            "last": _parse_meta_json(str(auto.get("walk_forward_last", "") or "")),
            "recent_runs": latest_walk_forward_runs(),
        },
        "calibration": calibration_panel(),
        "promotion_queue": promotion_queue(),
        "promotion_history": promotion_history(),
        "experiments": experiment_history(),
        "logs": research_activity_log(),
        "promotion_policy": "manual_only",
    }
