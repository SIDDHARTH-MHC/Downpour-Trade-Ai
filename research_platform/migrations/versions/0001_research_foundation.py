"""Research platform foundation: Timescale extension (optional) + meta table."""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_research_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    try:
        conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE"))
    except Exception:
        # Plain PostgreSQL: Phase 1 meta table still works; hypertables require Timescale (Phase 2+).
        pass

    op.create_table(
        "research_platform_meta",
        sa.Column("key", sa.String(length=128), primary_key=True),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.execute(
        sa.text(
            "INSERT INTO research_platform_meta (key, value) "
            "VALUES ('schema_phase', '1') ON CONFLICT (key) DO NOTHING"
        )
    )


def downgrade() -> None:
    op.drop_table("research_platform_meta")
    # Do not DROP EXTENSION timescaledb — may be shared; reversible migration stops at table drop.
