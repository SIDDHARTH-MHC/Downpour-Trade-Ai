"""Factory for research repository implementations."""

from __future__ import annotations

from functools import lru_cache

from research_platform.config import get_research_settings
from research_platform.repository.base import (
    NullResearchRepository,
    PostgresResearchRepository,
    ResearchRepository,
)


@lru_cache
def get_research_repository() -> ResearchRepository:
    settings = get_research_settings()
    if not settings.research_db_enabled:
        return NullResearchRepository()
    return PostgresResearchRepository()
