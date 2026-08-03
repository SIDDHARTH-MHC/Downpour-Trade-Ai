"""Phase 1 foundation metadata table."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from research_platform.db.base import ResearchBase


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ResearchPlatformMeta(ResearchBase):
    __tablename__ = "research_platform_meta"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
