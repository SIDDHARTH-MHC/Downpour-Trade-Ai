"""Scheduled research automation (MDS collector, DQ, walk-forward). No auto-promotion."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from api.db import Database
from engine.config import load_config
from engine.data import DataLayer
from research_platform.collector.mds_collector import MdsCollector
from research_platform.config import get_research_settings
from research_platform.dq.persist import persist_quality_report
from research_platform.dq.scanner import scan_ohlcv_frame
from research_platform.promotion_guard import assert_manual_promotion_only

logger = logging.getLogger("downpour.research.jobs")


def _utcnow_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def _set_meta(key: str, value: str) -> None:
    Database().set_meta(key, value)


def _parse_symbols(raw: str) -> list[str]:
    return [s.strip() for s in raw.split(",") if s.strip()]


def job_collect_historical_data() -> dict[str, Any]:
    """Incremental MDS ingest for configured T1 symbols."""
    assert_manual_promotion_only(context="job_collect_historical_data")
    settings = get_research_settings()
    if not settings.research_db_enabled:
        msg = "skipped: RESEARCH_DB_ENABLED=false"
        _set_meta("research_collector_last", msg)
        return {"status": "skipped", "reason": msg}

    symbols = _parse_symbols(settings.research_collector_symbols)
    coll = MdsCollector()
    results = []
    for sym in symbols:
        results.append(coll.ingest_symbol_candles(sym, "1h", bars=settings.research_collector_bars))
        results.append(coll.ingest_flows(sym, "1h"))
    summary = {"status": "ok", "symbols": symbols, "results": results, "at": _utcnow_str()}
    _set_meta("research_collector_last", json.dumps(summary, default=str))
    logger.info("research collector finished: %s symbols", len(symbols))
    return summary


def job_daily_data_quality_scan() -> dict[str, Any]:
    """Fetch live OHLCV and persist DQ reports (no repair)."""
    assert_manual_promotion_only(context="job_daily_data_quality_scan")
    settings = get_research_settings()
    symbols = _parse_symbols(settings.research_collector_symbols)
    data = DataLayer(load_config())
    reports = []
    for sym in symbols[:10]:
        df = data.get_ohlcv_history(sym, "1h", bars=settings.research_collector_bars, validate=False)
        report = scan_ohlcv_frame(df, symbol=sym, timeframe="1h")
        rid = persist_quality_report(report)
        reports.append({"symbol": sym, "severity": report["severity"], "report_id": rid})
    summary = {"status": "ok", "reports": reports, "at": _utcnow_str()}
    _set_meta("research_dq_last", json.dumps(summary, default=str))
    logger.info("research DQ scan finished: %s symbols", len(reports))
    return summary


def job_weekly_walk_forward() -> dict[str, Any]:
    """
    Run baseline walk-forward experiments and record artifacts.

    Does NOT promote config — manual approval only.
    """
    assert_manual_promotion_only(context="job_weekly_walk_forward")
    settings = get_research_settings()
    symbols = _parse_symbols(settings.research_wf_symbols)
    months = settings.research_wf_months

    from research.runner import compare_r0_variants
    from research_platform.experiments.registry import ExperimentRegistry

    results = compare_r0_variants(symbols, months=months)
    reg = ExperimentRegistry()
    run_ids = []
    for r in results:
        bundle = reg.create_run_bundle(
            experiment_code="SCHED-WF-B0-compare",
            variant=r.variant,
            run_kind="walk_forward_scheduled",
            symbols=[r.symbol],
            timeframe="1h",
            months=months,
            metrics=r.to_dict(),
        )
        run_ids.append(bundle["id"])

    summary = {
        "status": "ok",
        "promotion": "none — manual approval required",
        "runs": len(results),
        "artifact_ids": run_ids,
        "at": _utcnow_str(),
    }
    _set_meta("research_wf_last", json.dumps(summary, default=str))
    _enqueue_research_job("walk_forward", summary)
    logger.info("research walk-forward finished: %s runs (no promotion)", len(results))
    return summary


def _enqueue_research_job(kind: str, payload: dict[str, Any]) -> None:
    if not get_research_settings().research_db_enabled:
        return
    from research_platform.db.session import research_session
    from research_platform.models.platform_extras import ResearchJob

    with research_session() as session:
        if session is None:
            return
        session.add(
            ResearchJob(
                id=str(uuid.uuid4()),
                job_kind=kind,
                payload=payload,
                status="completed",
                created_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                progress="scheduled",
            )
        )


def research_automation_status() -> dict[str, Any]:
    db = Database()
    settings = get_research_settings()
    return {
        "enabled": settings.research_scheduler_enabled,
        "research_db_enabled": settings.research_db_enabled,
        "collector_last": db.get_meta("research_collector_last", ""),
        "dq_last": db.get_meta("research_dq_last", ""),
        "walk_forward_last": db.get_meta("research_wf_last", ""),
        "calibration_last_utc": db.get_meta("last_calibrated_utc", "never"),
        "calibration_schedule": "monthly via API scheduler (CALIBRATION_* settings)",
        "promotion_policy": "manual_only",
    }
