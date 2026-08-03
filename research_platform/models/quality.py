"""Data quality and lineage (Phase 4)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import BigInteger, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from research_platform.db.base import ResearchBase


class DataQualityReport(ResearchBase):
    __tablename__ = "data_quality_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    scope: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    symbol: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    series: Mapped[str] = mapped_column(String(64), nullable=False)
    timeframe: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    run_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    runner_version: Mapped[str] = mapped_column(String(32), nullable=False)
    expected_bars: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    actual_bars: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    missing_bars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duplicate_bars: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gap_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    corrupt_rows: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    checksum: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)


class DataQualityIssue(ResearchBase):
    __tablename__ = "data_quality_issues"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    report_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    issue_type: Mapped[str] = mapped_column(String(64), nullable=False)
    ts_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    ts_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    detail: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)


class DataRepair(ResearchBase):
    __tablename__ = "data_repairs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    exchange_id: Mapped[str] = mapped_column(String(32), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    series: Mapped[str] = mapped_column(String(64), nullable=False)
    timeframe: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    issue_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    repair_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    prior_dataset_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    new_dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    approved_by: Mapped[str] = mapped_column(String(128), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    applied_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    patch_manifest: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="logged", nullable=False)


class DataLineageEvent(ResearchBase):
    __tablename__ = "data_lineage_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    exchange_id: Mapped[str] = mapped_column(String(32), nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    series: Mapped[str] = mapped_column(String(64), nullable=False)
    event_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    collector_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    source_exchange: Mapped[str] = mapped_column(String(32), nullable=False)
    checksum_before: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    checksum_after: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    parent_event_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
