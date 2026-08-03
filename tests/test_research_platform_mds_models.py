"""Import tests for MDS SQLAlchemy models (no DB required)."""

from research_platform.models import (
    Candle,
    ExchangeEvent,
    FundingRate,
    IngestWatermark,
    LongShortRatio,
    MacroDaily,
    OpenInterest,
    UniverseRegistry,
)


def test_mds_model_tables():
    assert Candle.__tablename__ == "candles"
    assert FundingRate.__tablename__ == "funding"
    assert OpenInterest.__tablename__ == "open_interest"
    assert LongShortRatio.__tablename__ == "long_short_ratio"
    assert MacroDaily.__tablename__ == "macro_daily"
    assert UniverseRegistry.__tablename__ == "universe_registry"
    assert ExchangeEvent.__tablename__ == "exchange_events"
    assert IngestWatermark.__tablename__ == "ingest_watermarks"
