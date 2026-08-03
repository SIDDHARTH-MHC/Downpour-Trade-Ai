"""MDS collector — incremental ingest from DataLayer (Phase 5)."""

from __future__ import annotations

import time
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.dialects.postgresql import insert

from engine.config import load_config
from engine.data import DataLayer
from research_platform.config import get_research_settings

COLLECTOR_VERSION = "collector-1.0.0"
DEFAULT_EXCHANGE = "binance_usdm"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ms_ts(raw: int | float) -> datetime:
    return datetime.fromtimestamp(int(raw) / 1000, tz=timezone.utc)


class MdsCollector:
    """
    Fetches from live DataLayer and upserts into research MDS.

    Does not invoke engine.analyzer or change production paths.
    """

    def __init__(self, exchange_id: str = DEFAULT_EXCHANGE) -> None:
        self.exchange_id = exchange_id
        self._data = DataLayer(load_config())

    def enabled(self) -> bool:
        return get_research_settings().research_db_enabled

    def ingest_symbol_candles(
        self,
        symbol: str,
        timeframe: str = "1h",
        bars: int = 500,
    ) -> dict[str, Any]:
        if not self.enabled():
            return {"status": "skipped", "reason": "research_db_disabled"}

        from research_platform.db.session import research_session
        from research_platform.models.market import Candle
        from research_platform.models.dimensions import IngestWatermark

        df = self._data.get_ohlcv_history(symbol, timeframe, bars=bars, validate=False)
        if df.empty:
            return {"status": "empty", "symbol": symbol, "timeframe": timeframe}

        rows = []
        for _, row in df.iterrows():
            ts = _ms_ts(row["timestamp"])
            rows.append(
                {
                    "exchange_id": self.exchange_id,
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "ts": ts,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row.get("volume", 0)),
                    "quote_volume": float(row["volume"]) if "volume" in row else None,
                    "candle_source": "exchange_kline",
                }
            )

        with research_session() as session:
            if session is None:
                return {"status": "error", "reason": "no_session"}
            stmt = insert(Candle).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=["exchange_id", "symbol", "timeframe", "ts"],
                set_={
                    "open": stmt.excluded.open,
                    "high": stmt.excluded.high,
                    "low": stmt.excluded.low,
                    "close": stmt.excluded.close,
                    "volume": stmt.excluded.volume,
                },
            )
            session.execute(stmt)
            last_ts = rows[-1]["ts"]
            wm = {
                "source": "mds_collector",
                "exchange_id": self.exchange_id,
                "symbol": symbol,
                "series": f"candles_{timeframe}",
                "last_ts": last_ts,
                "updated_at": _utcnow(),
                "collector_version": COLLECTOR_VERSION,
            }
            session.execute(
                insert(IngestWatermark).values(wm).on_conflict_do_update(
                    index_elements=["source", "exchange_id", "symbol", "series"],
                    set_={
                        "last_ts": last_ts,
                        "updated_at": _utcnow(),
                        "collector_version": COLLECTOR_VERSION,
                    },
                )
            )

        self._record_lineage(symbol, f"candles_{timeframe}", len(rows))
        time.sleep(0.2)  # gentle rate limit between symbols
        return {"status": "ok", "symbol": symbol, "timeframe": timeframe, "rows": len(rows)}

    def _record_lineage(self, symbol: str, series: str, row_count: int) -> None:
        from research_platform.db.session import research_session
        from research_platform.models.quality import DataLineageEvent

        if not self.enabled():
            return
        with research_session() as session:
            if session is None:
                return
            session.add(
                DataLineageEvent(
                    id=str(uuid.uuid4()),
                    exchange_id=self.exchange_id,
                    symbol=symbol,
                    series=series,
                    event_kind="collector_ingest",
                    collector_version=COLLECTOR_VERSION,
                    source_exchange=self.exchange_id,
                    checksum_after=None,
                    payload={"row_count": row_count},
                    created_at=_utcnow(),
                )
            )

    def ingest_flows(self, symbol: str, timeframe: str = "1h") -> dict[str, Any]:
        if not self.enabled():
            return {"status": "skipped", "reason": "research_db_disabled"}

        from research_platform.db.session import research_session
        from research_platform.models.flows import FundingRate, LongShortRatio, OpenInterest
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        funding = self._data.get_funding_history(symbol, limit=500)
        oi_df = self._data.get_oi_history(symbol, timeframe, limit=500)
        ls = self._data.get_global_long_short_ratio(symbol, period=timeframe, limit=500)

        counts = {"funding": 0, "oi": 0, "ls": 0}
        with research_session() as session:
            if session is None:
                return {"status": "error", "reason": "no_session"}

            frows = []
            for item in funding:
                ts = _ms_ts(item.get("timestamp", 0))
                frows.append(
                    {
                        "exchange_id": self.exchange_id,
                        "symbol": symbol,
                        "ts": ts,
                        "funding_rate": float(item.get("fundingRate", 0)),
                        "mark_price": float(item["markPrice"]) if item.get("markPrice") else None,
                    }
                )
            if frows:
                stmt = pg_insert(FundingRate).values(frows)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["exchange_id", "symbol", "ts"],
                    set_={"funding_rate": stmt.excluded.funding_rate},
                )
                session.execute(stmt)
                counts["funding"] = len(frows)

            oi_rows = []
            if not oi_df.empty:
                for _, row in oi_df.iterrows():
                    oi_rows.append(
                        {
                            "exchange_id": self.exchange_id,
                            "symbol": symbol,
                            "timeframe": timeframe,
                            "ts": _ms_ts(row["timestamp"]),
                            "oi_contracts": float(row.get("openInterestAmount", 0) or 0),
                            "oi_value_usd": float(row.get("openInterestValue", 0) or 0) or None,
                        }
                    )
                if oi_rows:
                    stmt = pg_insert(OpenInterest).values(oi_rows)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["exchange_id", "symbol", "timeframe", "ts"],
                        set_={"oi_contracts": stmt.excluded.oi_contracts},
                    )
                    session.execute(stmt)
                    counts["oi"] = len(oi_rows)

            ls_rows = []
            for item in ls:
                ls_rows.append(
                    {
                        "exchange_id": self.exchange_id,
                        "symbol": symbol,
                        "period": timeframe,
                        "ts": _ms_ts(item.get("timestamp", 0)),
                        "long_short_ratio": float(item.get("longShortRatio", 1)),
                        "long_account": float(item["longAccount"]) if item.get("longAccount") else None,
                        "short_account": float(item["shortAccount"]) if item.get("shortAccount") else None,
                    }
                )
            if ls_rows:
                stmt = pg_insert(LongShortRatio).values(ls_rows)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["exchange_id", "symbol", "period", "ts"],
                    set_={"long_short_ratio": stmt.excluded.long_short_ratio},
                )
                session.execute(stmt)
                counts["ls"] = len(ls_rows)

        return {"status": "ok", "symbol": symbol, **counts}
