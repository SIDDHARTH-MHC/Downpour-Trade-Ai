"""Derivatives flow series."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Double, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from research_platform.db.base import ResearchBase


class FundingRate(ResearchBase):
    __tablename__ = "funding"
    __table_args__ = (UniqueConstraint("exchange_id", "symbol", "ts", name="uq_funding_ts"),)

    exchange_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    funding_rate: Mapped[float] = mapped_column(Double, nullable=False)
    mark_price: Mapped[Optional[float]] = mapped_column(Double, nullable=True)


class OpenInterest(ResearchBase):
    __tablename__ = "open_interest"
    __table_args__ = (
        UniqueConstraint("exchange_id", "symbol", "timeframe", "ts", name="uq_oi_ts"),
    )

    exchange_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(8), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    oi_contracts: Mapped[Optional[float]] = mapped_column(Double, nullable=True)
    oi_value_usd: Mapped[Optional[float]] = mapped_column(Double, nullable=True)


class LongShortRatio(ResearchBase):
    __tablename__ = "long_short_ratio"
    __table_args__ = (
        UniqueConstraint("exchange_id", "symbol", "period", "ts", name="uq_ls_ts"),
    )

    exchange_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    period: Mapped[str] = mapped_column(String(8), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    long_short_ratio: Mapped[float] = mapped_column(Double, nullable=False)
    long_account: Mapped[Optional[float]] = mapped_column(Double, nullable=True)
    short_account: Mapped[Optional[float]] = mapped_column(Double, nullable=True)
