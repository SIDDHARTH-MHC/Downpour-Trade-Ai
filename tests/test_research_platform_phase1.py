import os

import pytest

from research_platform.config import ResearchSettings, get_research_settings
from research_platform.repository.base import NullResearchRepository
from research_platform.repository.registry import get_research_repository


def test_research_settings_default_disabled():
    get_research_settings.cache_clear()
    os.environ.pop("RESEARCH_DB_ENABLED", None)
    settings = ResearchSettings()
    assert settings.research_db_enabled is False


def test_null_repository_when_disabled():
    get_research_settings.cache_clear()
    os.environ["RESEARCH_DB_ENABLED"] = "false"
    get_research_repository.cache_clear()
    repo = get_research_repository()
    assert isinstance(repo, NullResearchRepository)
    health = repo.health()
    assert health["enabled"] is False
    assert health["status"] == "disabled"


def test_null_repository_meta_raises():
    repo = NullResearchRepository()
    assert repo.get_platform_meta("schema_phase") is None
    with pytest.raises(RuntimeError):
        repo.set_platform_meta("k", "v")
