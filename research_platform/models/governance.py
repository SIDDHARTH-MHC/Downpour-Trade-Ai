"""Dataset versions, experiments, promotions (Phase 3+)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from research_platform.db.base import ResearchBase


class DatasetVersion(ResearchBase):
    __tablename__ = "dataset_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    exchange_id: Mapped[str] = mapped_column(String(32), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    tier: Mapped[str] = mapped_column(String(16), nullable=False)
    symbols: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    universe_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    timeframes: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    series_included: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    dataset_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    parquet_snapshot_uri: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_quality_report_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    validation_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    parent_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    frozen_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class Experiment(ResearchBase):
    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    hypothesis: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    roadmap_ref: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ExperimentRun(ResearchBase):
    __tablename__ = "experiment_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    experiment_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    variant: Mapped[str] = mapped_column(String(32), nullable=False)
    run_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    engine_git_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    engine_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    config_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    universe_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    universe_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    dataset_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    dataset_manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    feature_manifest: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    feature_manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    exchange_id: Mapped[str] = mapped_column(String(32), nullable=False)
    symbols: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(8), nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    promotion_class: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    promotion_decision: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    acceptance_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    artifacts_uri: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)


class EngineRelease(ResearchBase):
    __tablename__ = "engine_releases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    version_label: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    engine_git_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    released_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    release_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class PromotionRecord(ResearchBase):
    __tablename__ = "promotion_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engine_release_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    experiment_run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    feature_name: Mapped[str] = mapped_column(String(128), nullable=False)
    roadmap_id: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    promotion_class: Mapped[str] = mapped_column(String(8), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    decision_reason: Mapped[str] = mapped_column(Text, nullable=False)
    baseline_variant: Mapped[str] = mapped_column(String(32), default="B0", nullable=False)
    metrics_delta: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    integration_scope: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String), nullable=True)
    rollback_plan: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str] = mapped_column(String(128), nullable=False)
    approved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    prior_config_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    new_config_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class EngineReleaseAttribution(ResearchBase):
    __tablename__ = "engine_release_attribution"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engine_release_id: Mapped[str] = mapped_column(String(36), nullable=False)
    experiment_run_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    method: Mapped[str] = mapped_column(String(64), nullable=False)
    lane_contribution_pct: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    attribution_details: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    disclaimer: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
