"""Run Alembic migrations for the research database."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from research_platform.config import get_research_settings


def migrations_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "migrations"


def run_alembic(*args: str) -> int:
    settings = get_research_settings()
    env = {
        **dict(__import__("os").environ),
        "RESEARCH_DATABASE_URL": settings.research_database_url,
    }
    cmd = [
        sys.executable,
        "-m",
        "alembic",
        "-c",
        str(migrations_dir() / "alembic.ini"),
        *args,
    ]
    return subprocess.call(cmd, cwd=str(migrations_dir()), env=env)


def upgrade(revision: str = "head") -> int:
    return run_alembic("upgrade", revision)


def current() -> int:
    return run_alembic("current")


def downgrade(revision: str = "-1") -> int:
    return run_alembic("downgrade", revision)
