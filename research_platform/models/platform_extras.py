"""Feature store, tags, jobs, capability matrix (Phases 7–8)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from research_platform.db.base import ResearchBase


class FeatureStoreEntry(ResearchBase):
    __tablename__ = "feature_store_entries"

    feature_set_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    engine_git_sha: Mapped[str] = mapped_column(String(64), nullable=False)
    config_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    feature_manifest_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    catalog_version: Mapped[str] = mapped_column(String(32), nullable=False)
    dataset_version_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    storage_uri: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    build_policy: Mapped[str] = mapped_column(String(32), default="cache", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ResearchTag(ResearchBase):
    __tablename__ = "research_tags"

    slug: Mapped[str] = mapped_column(String(64), primary_key=True)
    label: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ExperimentTag(ResearchBase):
    __tablename__ = "experiment_tags"

    experiment_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tag_slug: Mapped[str] = mapped_column(String(64), primary_key=True)


class EngineCapabilityMatrix(ResearchBase):
    __tablename__ = "engine_capability_matrix"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    engine_release_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    version_label: Mapped[str] = mapped_column(String(32), nullable=False)
    capabilities: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)
    capability_details: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ResearchJob(ResearchBase):
    __tablename__ = "research_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    job_kind: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    progress: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
