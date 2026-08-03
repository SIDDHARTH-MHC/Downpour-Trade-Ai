from research_platform.repository.base import NullResearchRepository, ResearchRepository
from research_platform.repository.registry import get_research_repository

__all__ = [
    "NullResearchRepository",
    "ResearchRepository",
    "get_research_repository",
]
