"""OHLCV candles (hypertable on ts)."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Double, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from research_platform.db.base import ResearchBase


class Candle(ResearchBase):
    __tablename__ = "candles"
    __table_args__ = (
        UniqueConstraint("exchange_id", "symbol", "timeframe", "ts", name="uq_candles_bar"),
    )

    exchange_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    timeframe: Mapped[str] = mapped_column(String(8), primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), primary_key=True)
    open: Mapped[float] = mapped_column(Double, nullable=False)
    high: Mapped[float] = mapped_column(Double, nullable=False)
    low: Mapped[float] = mapped_column(Double, nullable=False)
    close: Mapped[float] = mapped_column(Double, nullable=False)
    volume: Mapped[float] = mapped_column(Double, nullable=False)
    quote_volume: Mapped[Optional[float]] = mapped_column(Double, nullable=True)
    candle_source: Mapped[str] = mapped_column(String(32), default="exchange_kline", nullable=False)
