"""Persist DQ reports to research DB (reporting only)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any


def persist_quality_report(report: dict[str, Any]) -> str | None:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return None

    from research_platform.db.session import research_session
    from research_platform.models.quality import DataQualityIssue, DataQualityReport

    report_id = report.get("id") or str(uuid.uuid4())
    run_at = report.get("run_at")
    if isinstance(run_at, str):
        run_at_dt = datetime.fromisoformat(run_at.replace("Z", "+00:00"))
    else:
        run_at_dt = datetime.now(timezone.utc)

    with research_session() as session:
        if session is None:
            return None
        session.add(
            DataQualityReport(
                id=report_id,
                scope=report.get("scope", "symbol_series"),
                exchange_id=report.get("exchange_id"),
                symbol=report.get("symbol"),
                series=report.get("series", "candles_1h"),
                timeframe=report.get("timeframe"),
                run_at=run_at_dt,
                runner_version=report.get("runner_version", "dq-1.0.0"),
                expected_bars=report.get("expected_bars"),
                actual_bars=report.get("actual_bars"),
                missing_bars=int(report.get("missing_bars", 0)),
                duplicate_bars=int(report.get("duplicate_bars", 0)),
                gap_count=int(report.get("gap_count", 0)),
                corrupt_rows=int(report.get("corrupt_rows", 0)),
                checksum=report.get("checksum"),
                details=report.get("details", {}),
                severity=report.get("severity", "ok"),
                status=report.get("status", "open"),
            )
        )
        for issue in report.get("issues") or []:
            session.add(
                DataQualityIssue(
                    id=str(uuid.uuid4()),
                    report_id=report_id,
                    issue_type=issue.get("issue_type", "unknown"),
                    severity=issue.get("severity", "warning"),
                    detail=issue,
                )
            )
    return report_id
