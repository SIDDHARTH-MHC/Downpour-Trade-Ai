"""Alembic revision 0003 — governance, DQ, feature store, jobs (Phases 3–4, 7–8 tables)."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0003_research_governance"
down_revision: Union[str, None] = "0002_mds_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dataset_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("version_code", sa.String(64), nullable=False, unique=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("exchange_id", sa.String(32), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("tier", sa.String(16), nullable=False),
        sa.Column("symbols", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("universe_hash", sa.String(64), nullable=False),
        sa.Column("timeframes", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("series_included", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("dataset_hash", sa.String(64), nullable=False),
        sa.Column("dataset_manifest", postgresql.JSONB(), nullable=False),
        sa.Column("parquet_snapshot_uri", sa.Text(), nullable=True),
        sa.Column("data_quality_report_id", sa.String(36), nullable=True),
        sa.Column("validation_passed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("parent_version_id", sa.String(36), nullable=True),
        sa.Column("created_by", sa.String(128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("frozen_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "experiments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=True),
        sa.Column("roadmap_ref", sa.String(32), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "experiment_runs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("experiment_id", sa.String(36), nullable=False),
        sa.Column("variant", sa.String(32), nullable=False),
        sa.Column("run_kind", sa.String(32), nullable=False),
        sa.Column("engine_git_sha", sa.String(64), nullable=False),
        sa.Column("engine_version", sa.String(32), nullable=True),
        sa.Column("config_hash", sa.String(64), nullable=False),
        sa.Column("config_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("universe_hash", sa.String(64), nullable=False),
        sa.Column("universe_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("dataset_hash", sa.String(64), nullable=False),
        sa.Column("dataset_manifest", postgresql.JSONB(), nullable=False),
        sa.Column("dataset_version_id", sa.String(36), nullable=True),
        sa.Column("feature_manifest", postgresql.JSONB(), nullable=False),
        sa.Column("feature_manifest_hash", sa.String(64), nullable=False),
        sa.Column("exchange_id", sa.String(32), nullable=False),
        sa.Column("symbols", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("timeframe", sa.String(8), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("months", sa.Integer(), nullable=True),
        sa.Column("promotion_class", sa.String(8), nullable=True),
        sa.Column("promotion_decision", sa.String(32), nullable=True),
        sa.Column("acceptance_reason", sa.Text(), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("metrics", postgresql.JSONB(), nullable=False),
        sa.Column("artifacts_uri", sa.Text(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_experiment_runs_experiment", "experiment_runs", ["experiment_id"])
    op.create_index("ix_experiment_runs_dataset_version", "experiment_runs", ["dataset_version_id"])

    op.create_table(
        "engine_releases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("version_label", sa.String(32), nullable=False, unique=True),
        sa.Column("engine_git_sha", sa.String(64), nullable=False),
        sa.Column("config_hash", sa.String(64), nullable=False),
        sa.Column("released_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("release_notes", sa.Text(), nullable=True),
    )
    op.create_table(
        "promotion_records",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("engine_release_id", sa.String(36), nullable=True),
        sa.Column("experiment_run_id", sa.String(36), nullable=True),
        sa.Column("dataset_version_id", sa.String(36), nullable=True),
        sa.Column("feature_name", sa.String(128), nullable=False),
        sa.Column("roadmap_id", sa.String(32), nullable=True),
        sa.Column("promotion_class", sa.String(8), nullable=False),
        sa.Column("decision", sa.String(32), nullable=False),
        sa.Column("decision_reason", sa.Text(), nullable=False),
        sa.Column("baseline_variant", sa.String(32), nullable=False, server_default="B0"),
        sa.Column("metrics_delta", postgresql.JSONB(), nullable=False),
        sa.Column("integration_scope", postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column("rollback_plan", sa.Text(), nullable=True),
        sa.Column("approved_by", sa.String(128), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("prior_config_hash", sa.String(64), nullable=True),
        sa.Column("new_config_hash", sa.String(64), nullable=False),
    )
    op.create_table(
        "engine_release_attribution",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("engine_release_id", sa.String(36), nullable=False),
        sa.Column("experiment_run_id", sa.String(36), nullable=True),
        sa.Column("dataset_version_id", sa.String(36), nullable=True),
        sa.Column("method", sa.String(64), nullable=False),
        sa.Column("lane_contribution_pct", postgresql.JSONB(), nullable=False),
        sa.Column("attribution_details", postgresql.JSONB(), nullable=True),
        sa.Column("disclaimer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "data_quality_reports",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("scope", sa.String(32), nullable=False),
        sa.Column("exchange_id", sa.String(32), nullable=True),
        sa.Column("symbol", sa.String(32), nullable=True),
        sa.Column("series", sa.String(64), nullable=False),
        sa.Column("timeframe", sa.String(8), nullable=True),
        sa.Column("dataset_version_id", sa.String(36), nullable=True),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("runner_version", sa.String(32), nullable=False),
        sa.Column("expected_bars", sa.BigInteger(), nullable=True),
        sa.Column("actual_bars", sa.BigInteger(), nullable=True),
        sa.Column("missing_bars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duplicate_bars", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("gap_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("corrupt_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("checksum", sa.String(128), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
    )
    op.create_table(
        "data_quality_issues",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("report_id", sa.String(36), nullable=False),
        sa.Column("issue_type", sa.String(64), nullable=False),
        sa.Column("ts_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ts_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("detail", postgresql.JSONB(), nullable=True),
        sa.Column("severity", sa.String(16), nullable=False),
    )
    op.create_index("ix_dq_issues_report", "data_quality_issues", ["report_id"])

    op.create_table(
        "data_repairs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("exchange_id", sa.String(32), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=False),
        sa.Column("series", sa.String(64), nullable=False),
        sa.Column("timeframe", sa.String(8), nullable=True),
        sa.Column("issue_id", sa.String(36), nullable=True),
        sa.Column("repair_kind", sa.String(64), nullable=False),
        sa.Column("prior_dataset_hash", sa.String(64), nullable=True),
        sa.Column("new_dataset_version_id", sa.String(36), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("approved_by", sa.String(128), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("patch_manifest", postgresql.JSONB(), nullable=True),
        sa.Column("status", sa.String(32), nullable=False, server_default="logged"),
    )
    op.create_table(
        "data_lineage_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("exchange_id", sa.String(32), nullable=False),
        sa.Column("symbol", sa.String(32), nullable=True),
        sa.Column("series", sa.String(64), nullable=False),
        sa.Column("event_kind", sa.String(64), nullable=False),
        sa.Column("collector_version", sa.String(32), nullable=True),
        sa.Column("source_exchange", sa.String(32), nullable=False),
        sa.Column("checksum_before", sa.String(128), nullable=True),
        sa.Column("checksum_after", sa.String(128), nullable=True),
        sa.Column("parent_event_id", sa.String(36), nullable=True),
        sa.Column("dataset_version_id", sa.String(36), nullable=True),
        sa.Column("payload", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "feature_store_entries",
        sa.Column("feature_set_id", sa.String(64), primary_key=True),
        sa.Column("engine_git_sha", sa.String(64), nullable=False),
        sa.Column("config_hash", sa.String(64), nullable=False),
        sa.Column("feature_manifest_hash", sa.String(64), nullable=False),
        sa.Column("catalog_version", sa.String(32), nullable=False),
        sa.Column("dataset_version_id", sa.String(36), nullable=True),
        sa.Column("storage_uri", sa.Text(), nullable=True),
        sa.Column("build_policy", sa.String(32), nullable=False, server_default="cache"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "research_tags",
        sa.Column("slug", sa.String(64), primary_key=True),
        sa.Column("label", sa.String(128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_table(
        "experiment_tags",
        sa.Column("experiment_id", sa.String(36), primary_key=True),
        sa.Column("tag_slug", sa.String(64), primary_key=True),
    )
    op.create_table(
        "engine_capability_matrix",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("engine_release_id", sa.String(36), nullable=False),
        sa.Column("version_label", sa.String(32), nullable=False),
        sa.Column("capabilities", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("capability_details", postgresql.JSONB(), nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_capability_release", "engine_capability_matrix", ["engine_release_id"])

    op.create_table(
        "research_jobs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("job_kind", sa.String(64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_by", sa.String(128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("progress", sa.String(256), nullable=True),
    )

    op.execute(
        sa.text(
            "UPDATE research_platform_meta SET value = '3', updated_at = now() "
            "WHERE key = 'schema_phase'"
        )
    )

    # Seed default research tags
    op.execute(
        sa.text(
            "INSERT INTO research_tags (slug, label) VALUES "
            "('liquidity', 'Liquidity'), ('macro', 'Macro'), ('flow', 'Flow'), "
            "('structure', 'Structure'), ('vwap', 'VWAP'), ('calibration', 'Calibration'), "
            "('risk', 'Risk') ON CONFLICT (slug) DO NOTHING"
        )
    )


def downgrade() -> None:
    for t in (
        "research_jobs",
        "engine_capability_matrix",
        "experiment_tags",
        "research_tags",
        "feature_store_entries",
        "data_lineage_events",
        "data_repairs",
        "data_quality_issues",
        "data_quality_reports",
        "engine_release_attribution",
        "promotion_records",
        "engine_releases",
        "experiment_runs",
        "experiments",
        "dataset_versions",
    ):
        op.drop_table(t)
    op.execute(
        sa.text(
            "UPDATE research_platform_meta SET value = '2', updated_at = now() "
            "WHERE key = 'schema_phase'"
        )
    )
