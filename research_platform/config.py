"""Research platform database configuration (separate from api DATABASE_URL / SQLite)."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ResearchSettings(BaseSettings):
    """
    Feature-flagged research database.

    Production API continues using SQLite via api.settings.Settings.database_url.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    research_db_enabled: bool = Field(default=False, alias="RESEARCH_DB_ENABLED")
    research_database_url: str = Field(
        default="postgresql+psycopg://downpour:downpour@localhost:5433/downpour_research",
        alias="RESEARCH_DATABASE_URL",
    )
    research_db_pool_size: int = Field(default=2, alias="RESEARCH_DB_POOL_SIZE")
    research_db_max_overflow: int = Field(default=2, alias="RESEARCH_DB_MAX_OVERFLOW")
    research_db_echo: bool = Field(default=False, alias="RESEARCH_DB_ECHO")
    research_internal_api_enabled: bool = Field(default=False, alias="RESEARCH_INTERNAL_API_ENABLED")
    research_artifact_root: str = Field(default="research/artifacts", alias="RESEARCH_ARTIFACT_ROOT")

    @model_validator(mode="after")
    def _require_url_when_enabled(self) -> ResearchSettings:
        if self.research_db_enabled and not self.research_database_url.strip():
            raise ValueError("RESEARCH_DATABASE_URL is required when RESEARCH_DB_ENABLED=true")
        return self


@lru_cache
def get_research_settings() -> ResearchSettings:
    return ResearchSettings()
