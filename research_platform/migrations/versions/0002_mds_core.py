"""MDS core tables + Timescale hypertables (Phase 2)."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0002_mds_core"
down_revision: Union[str, None] = "0001_research_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TS_TABLES = (
    ("candles", "ts"),
    ("funding", "ts"),
    ("open_interest", "ts"),
    ("long_short_ratio", "ts"),
    ("macro_daily", "ts"),
)


def _try_hypertable(table: str, time_column: str) -> None:
    conn = op.get_bind()
    try:
        conn.execute(
            sa.text(
                f"SELECT create_hypertable('{table}', '{time_column}', "
                "if_not_exists => TRUE, migrate_data => TRUE)"
            )
        )
    except Exception:
        pass


def _try_compression(table: str) -> None:
    conn = op.get_bind()
    try:
        conn.execute(sa.text(f"ALTER TABLE {table} SET (timescaledb.compress = true)"))
        conn.execute(
            sa.text(
                f"SELECT add_compression_policy('{table}', INTERVAL '30 days', if_not_exists => TRUE)"
            )
        )
    except Exception:
        pass


def _try_retention(table: str, interval: str) -> None:
    conn = op.get_bind()
    try:
        conn.execute(
            sa.text(
                f"SELECT add_retention_policy('{table}', INTERVAL '{interval}', if_not_exists => TRUE)"
            )
        )
    except Exception:
        pass


def upgrade() -> None:
    op.create_table(
        "candles",
        sa.Column("exchange_id", sa.String(length=32), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=8), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("open", sa.Double(), nullable=False),
        sa.Column("high", sa.Double(), nullable=False),
        sa.Column("low", sa.Double(), nullable=False),
        sa.Column("close", sa.Double(), nullable=False),
        sa.Column("volume", sa.Double(), nullable=False),
        sa.Column("quote_volume", sa.Double(), nullable=True),
        sa.Column("candle_source", sa.String(length=32), nullable=False, server_default="exchange_kline"),
        sa.PrimaryKeyConstraint("exchange_id", "symbol", "timeframe", "ts", name="pk_candles"),
        sa.UniqueConstraint("exchange_id", "symbol", "timeframe", "ts", name="uq_candles_bar"),
    )
    op.create_index("ix_candles_lookup", "candles", ["exchange_id", "symbol", "timeframe", "ts"])

    op.create_table(
        "funding",
        sa.Column("exchange_id", sa.String(length=32), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("funding_rate", sa.Double(), nullable=False),
        sa.Column("mark_price", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("exchange_id", "symbol", "ts", name="pk_funding"),
        sa.UniqueConstraint("exchange_id", "symbol", "ts", name="uq_funding_ts"),
    )
    op.create_index("ix_funding_lookup", "funding", ["exchange_id", "symbol", "ts"])

    op.create_table(
        "open_interest",
        sa.Column("exchange_id", sa.String(length=32), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("timeframe", sa.String(length=8), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("oi_contracts", sa.Double(), nullable=True),
        sa.Column("oi_value_usd", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("exchange_id", "symbol", "timeframe", "ts", name="pk_open_interest"),
        sa.UniqueConstraint("exchange_id", "symbol", "timeframe", "ts", name="uq_oi_ts"),
    )
    op.create_index("ix_oi_lookup", "open_interest", ["exchange_id", "symbol", "timeframe", "ts"])

    op.create_table(
        "long_short_ratio",
        sa.Column("exchange_id", sa.String(length=32), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("period", sa.String(length=8), nullable=False),
        sa.Column("ts", sa.DateTime(timezone=True), nullable=False),
        sa.Column("long_short_ratio", sa.Double(), nullable=False),
        sa.Column("long_account", sa.Double(), nullable=True),
        sa.Column("short_account", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("exchange_id", "symbol", "period", "ts", name="pk_long_short_ratio"),
        sa.UniqueConstraint("exchange_id", "symbol", "period", "ts", name="uq_ls_ts"),
    )
    op.create_index("ix_ls_lookup", "long_short_ratio", ["exchange_id", "symbol", "period", "ts"])

    op.create_table(
        "macro_daily",
        sa.Column("series", sa.String(length=64), nullable=False),
        sa.Column("ts", sa.Date(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("value", sa.Double(), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("series", "ts", "revision", name="pk_macro_daily"),
        sa.UniqueConstraint("series", "ts", "revision", name="uq_macro_daily"),
    )

    op.create_table(
        "universe_registry",
        sa.Column("exchange_id", sa.String(length=32), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("tier", sa.String(length=8), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("listed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delisted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("universe_code", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("exchange_id", "symbol", name="pk_universe_registry"),
    )

    op.create_table(
        "exchange_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("exchange_id", sa.String(length=32), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("symbol_from", sa.String(length=32), nullable=True),
        sa.Column("symbol_to", sa.String(length=32), nullable=True),
        sa.Column("effective_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("announced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("affects_backtest", sa.Boolean(), nullable=False, server_default="true"),
        sa.PrimaryKeyConstraint("id", name="pk_exchange_events"),
    )
    op.create_index("ix_exchange_events_exchange", "exchange_events", ["exchange_id", "effective_at"])

    op.create_table(
        "ingest_watermarks",
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("exchange_id", sa.String(length=32), nullable=False),
        sa.Column("symbol", sa.String(length=32), nullable=False),
        sa.Column("series", sa.String(length=64), nullable=False),
        sa.Column("last_ts", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("collector_version", sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint("source", "exchange_id", "symbol", "series", name="pk_ingest_watermarks"),
    )

    for table, tcol in TS_TABLES:
        _try_hypertable(table, tcol)

    for table in ("candles", "funding", "open_interest", "long_short_ratio", "macro_daily"):
        _try_compression(table)

    # 1m candles policy placeholder: if timeframe=1m ingested later, retention applies at table level
    # No global drop on candles — per MDS v3 T1 1h retained forever; 1m optional short retention in Phase 5+

    op.execute(
        sa.text(
            "UPDATE research_platform_meta SET value = '2', updated_at = now() "
            "WHERE key = 'schema_phase'"
        )
    )


def downgrade() -> None:
    op.drop_table("ingest_watermarks")
    op.drop_table("exchange_events")
    op.drop_table("universe_registry")
    op.drop_table("macro_daily")
    op.drop_table("long_short_ratio")
    op.drop_table("open_interest")
    op.drop_table("funding")
    op.drop_table("candles")
    op.execute(
        sa.text(
            "UPDATE research_platform_meta SET value = '1', updated_at = now() "
            "WHERE key = 'schema_phase'"
        )
    )
