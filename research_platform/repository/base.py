"""Repository abstraction for the research data platform (MDS)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ResearchRepository(ABC):
    """
    Read/write boundary for research MDS.

    Runtime engine and api/db.py SQLite are intentionally outside this interface.
    """

    @abstractmethod
    def enabled(self) -> bool:
        ...

    @abstractmethod
    def health(self) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_platform_meta(self, key: str) -> str | None:
        ...

    @abstractmethod
    def set_platform_meta(self, key: str, value: str) -> None:
        ...


class NullResearchRepository(ResearchRepository):
    """No-op when RESEARCH_DB_ENABLED=false (default)."""

    def enabled(self) -> bool:
        return False

    def health(self) -> dict[str, Any]:
        return {
            "enabled": False,
            "status": "disabled",
            "message": "Set RESEARCH_DB_ENABLED=true and RESEARCH_DATABASE_URL to use the research database.",
        }

    def get_platform_meta(self, key: str) -> str | None:
        return None

    def set_platform_meta(self, key: str, value: str) -> None:
        raise RuntimeError("Research database is disabled")


class PostgresResearchRepository(ResearchRepository):
    def enabled(self) -> bool:
        return True

    def health(self) -> dict[str, Any]:
        from research_platform.db.engine import postgres_server_info, timescale_available
        from research_platform.db.engine import get_research_engine

        engine = get_research_engine()
        info = postgres_server_info(engine)
        if info.get("error"):
            return {"enabled": True, "status": "error", **info}
        return {
            "enabled": True,
            "status": "ok",
            "timescaledb": timescale_available(engine),
            **info,
        }

    def get_platform_meta(self, key: str) -> str | None:
        from research_platform.models.meta import ResearchPlatformMeta
        from research_platform.db.session import research_session

        with research_session() as session:
            if session is None:
                return None
            row = session.get(ResearchPlatformMeta, key)
            return row.value if row else None

    def set_platform_meta(self, key: str, value: str) -> None:
        from research_platform.models.meta import ResearchPlatformMeta
        from research_platform.db.session import research_session

        with research_session() as session:
            if session is None:
                raise RuntimeError("Research session unavailable")
            row = session.get(ResearchPlatformMeta, key)
            if row is None:
                session.add(ResearchPlatformMeta(key=key, value=value))
            else:
                row.value = value
