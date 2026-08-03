"""CLI helpers for research platform database (Phase 1)."""

from __future__ import annotations

import json

from research_platform.config import get_research_settings
from research_platform.db.engine import create_research_engine, dispose_research_engine
from research_platform.migrations import runner as migration_runner
from research_platform.repository.registry import get_research_repository


def cmd_status() -> dict:
    settings = get_research_settings()
    repo = get_research_repository()
    return {
        "research_db_enabled": settings.research_db_enabled,
        "research_database_url": _redact_url(settings.research_database_url),
        **repo.health(),
    }


def cmd_migrate() -> int:
    settings = get_research_settings()
    if not settings.research_db_enabled:
        raise SystemExit("RESEARCH_DB_ENABLED must be true to run migrations.")
    create_research_engine(force_new=True)
    code = migration_runner.upgrade("head")
    dispose_research_engine()
    return code


def cmd_meta_get(key: str) -> str | None:
    return get_research_repository().get_platform_meta(key)


def _redact_url(url: str) -> str:
    if "@" not in url:
        return url
    prefix, rest = url.split("@", 1)
    if "://" in prefix:
        scheme, _ = prefix.split("://", 1)
        return f"{scheme}://***@{rest}"
    return url


def print_status() -> None:
    print(json.dumps(cmd_status(), indent=2))
