"""SQLAlchemy engine factory for the research PostgreSQL / TimescaleDB."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from research_platform.config import get_research_settings

_engine: Engine | None = None


def create_research_engine(*, force_new: bool = False) -> Engine | None:
    global _engine
    settings = get_research_settings()
    if not settings.research_db_enabled:
        return None
    if _engine is not None and not force_new:
        return _engine
    if force_new and _engine is not None:
        _engine.dispose()
        _engine = None

    _engine = create_engine(
        settings.research_database_url,
        pool_pre_ping=True,
        pool_size=settings.research_db_pool_size,
        max_overflow=settings.research_db_max_overflow,
        echo=settings.research_db_echo,
        future=True,
    )
    return _engine


def get_research_engine() -> Engine | None:
    if _engine is None:
        return create_research_engine()
    return _engine


def dispose_research_engine() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None


def timescale_available(engine: Engine | None = None) -> bool:
    eng = engine or get_research_engine()
    if eng is None:
        return False
    try:
        with eng.connect() as conn:
            row = conn.execute(
                text(
                    "SELECT EXISTS("
                    "  SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'"
                    ")"
                )
            ).scalar()
            return bool(row)
    except Exception:
        return False


def postgres_server_info(engine: Engine | None = None) -> dict[str, Any]:
    eng = engine or get_research_engine()
    if eng is None:
        return {"enabled": False}
    try:
        with eng.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            db = conn.execute(text("SELECT current_database()")).scalar()
            return {
                "enabled": True,
                "database": db,
                "version": version,
                "timescaledb": timescale_available(eng),
            }
    except Exception as exc:  # noqa: BLE001
        return {"enabled": True, "error": str(exc)}
