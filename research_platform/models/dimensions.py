"""Shared macro series and registry dimensions."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from sqlalchemy import Boolean, Date, DateTime, Double, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from research_platform.db.base import ResearchBase


class MacroDaily(ResearchBase):
    __tablename__ = "macro_daily"
    __table_args__ = (UniqueConstraint("series", "ts", "revision", name="uq_macro_daily"),)

    series: Mapped[str] = mapped_column(String(64), primary_key=True)
    ts: Mapped[date] = mapped_column(Date, primary_key=True)
    revision: Mapped[int] = mapped_column(primary_key=True, default=0)
    value: Mapped[float] = mapped_column(Double, nullable=False)
    source: Mapped[str] = mapped_column(String(64), nullable=False)


class UniverseRegistry(ResearchBase):
    __tablename__ = "universe_registry"

    exchange_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    tier: Mapped[str] = mapped_column(String(8), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    listed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    delisted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    universe_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)


class ExchangeEvent(ResearchBase):
    __tablename__ = "exchange_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    exchange_id: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    symbol_from: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    symbol_to: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    effective_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    announced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    affects_backtest: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class IngestWatermark(ResearchBase):
    __tablename__ = "ingest_watermarks"

    source: Mapped[str] = mapped_column(String(64), primary_key=True)
    exchange_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    series: Mapped[str] = mapped_column(String(64), primary_key=True)
    last_ts: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    collector_version: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
