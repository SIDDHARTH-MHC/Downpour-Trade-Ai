"""Market data access: live (DataLayer) vs history (MDS) — Phase 6."""

from __future__ import annotations

from typing import Any

import pandas as pd

from engine.config import EngineConfig, load_config
from engine.data import DataLayer


class MarketDataRepository:
    """
    Research-facing data boundary. Production analyze/scan keeps using DataLayer directly.
    """

    def __init__(self, config: EngineConfig | None = None, exchange_id: str = "binance_usdm") -> None:
        self._cfg = config or load_config()
        self._live = DataLayer(self._cfg)
        self.exchange_id = exchange_id

    def live(self) -> DataLayer:
        return self._live

    def history_enabled(self) -> bool:
        from research_platform.config import get_research_settings

        return get_research_settings().research_db_enabled

    def history_candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 500,
    ) -> pd.DataFrame:
        if not self.history_enabled():
            return self._live.get_ohlcv_history(symbol, timeframe, bars=limit, validate=False)

        from sqlalchemy import select

        from research_platform.db.session import research_session
        from research_platform.models.market import Candle

        with research_session() as session:
            if session is None:
                return self._live.get_ohlcv_history(symbol, timeframe, bars=limit, validate=False)
            q = (
                select(Candle)
                .where(
                    Candle.exchange_id == self.exchange_id,
                    Candle.symbol == symbol,
                    Candle.timeframe == timeframe,
                )
                .order_by(Candle.ts.desc())
                .limit(limit)
            )
            rows = session.scalars(q).all()
        if not rows:
            return self._live.get_ohlcv_history(symbol, timeframe, bars=limit, validate=False)

        rows = list(reversed(rows))
        data = {
            "timestamp": [int(r.ts.timestamp() * 1000) for r in rows],
            "open": [r.open for r in rows],
            "high": [r.high for r in rows],
            "low": [r.low for r in rows],
            "close": [r.close for r in rows],
            "volume": [r.volume for r in rows],
        }
        return pd.DataFrame(data)

    def history_funding(self, symbol: str, limit: int = 500) -> list[dict[str, Any]]:
        if not self.history_enabled():
            return self._live.get_funding_history(symbol, limit=limit)

        from sqlalchemy import select

        from research_platform.db.session import research_session
        from research_platform.models.flows import FundingRate

        with research_session() as session:
            if session is None:
                return self._live.get_funding_history(symbol, limit=limit)
            q = (
                select(FundingRate)
                .where(FundingRate.exchange_id == self.exchange_id, FundingRate.symbol == symbol)
                .order_by(FundingRate.ts.desc())
                .limit(limit)
            )
            rows = list(reversed(session.scalars(q).all()))
        if not rows:
            return self._live.get_funding_history(symbol, limit=limit)
        return [
            {
                "timestamp": int(r.ts.timestamp() * 1000),
                "fundingRate": r.funding_rate,
                "markPrice": r.mark_price,
            }
            for r in rows
        ]
