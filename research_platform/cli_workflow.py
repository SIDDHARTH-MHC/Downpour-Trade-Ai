"""End-to-end research MDS workflows for the CLI."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE_FILE = ROOT / "deploy" / "research" / "docker-compose.yml"

DEFAULT_DATABASE_URL = "postgresql+psycopg://downpour:downpour@localhost:5433/downpour_research"


def _run(cmd: list[str], *, cwd: Path | None = None) -> int:
    return subprocess.call(cmd, cwd=str(cwd or ROOT))


def docker_db_up() -> int:
    if not COMPOSE_FILE.is_file():
        raise SystemExit(f"Missing {COMPOSE_FILE}")
    return _run(["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"])


def docker_db_down() -> int:
    if not COMPOSE_FILE.is_file():
        raise SystemExit(f"Missing {COMPOSE_FILE}")
    return _run(["docker", "compose", "-f", str(COMPOSE_FILE), "down"])


def enable_research_env(database_url: str | None = None) -> None:
    """Enable research DB for this process (does not write .env)."""
    os.environ["RESEARCH_DB_ENABLED"] = "true"
    os.environ["RESEARCH_DATABASE_URL"] = database_url or DEFAULT_DATABASE_URL
    from research_platform.config import get_research_settings
    from research_platform.repository.registry import get_research_repository

    get_research_settings.cache_clear()
    get_research_repository.cache_clear()


def print_env_hint() -> None:
    print("Export for your shell (or add to .env):")
    print(f"  export RESEARCH_DB_ENABLED=true")
    print(f"  export RESEARCH_DATABASE_URL={DEFAULT_DATABASE_URL}")
    print("Optional internal dashboard APIs:")
    print("  export RESEARCH_INTERNAL_API_ENABLED=true")


def guide_text() -> str:
    return """
Research MDS — CLI workflow (production engine unchanged)

  1. Start Timescale (local)
       python cli.py research db up

  2. One-shot setup (enable env in-process + migrate)
       python cli.py research setup --enable --db-up --migrate

  3. Status
       python cli.py research db status

  4. Ingest market data into MDS
       python cli.py research collect --symbols BTC/USDT,ETH/USDT

  5. Data quality (stdout report)
       python cli.py research dq-scan --symbol BTC/USDT

  6. Walk-forward + reproducibility artifact
       python cli.py research walk-forward --compare --record

  7. Full local smoke test
       python cli.py research quickstart

  8. Stop database container
       python cli.py research db down

Docs: docs/RESEARCH_PLATFORM.md, docs/HISTORICAL_DATA_ARCHITECTURE.md
""".strip()


def run_quickstart(
    *,
    db_up: bool = True,
    migrate: bool = True,
    collect: bool = True,
    dq: bool = True,
    database_url: str | None = None,
) -> int:
    enable_research_env(database_url)
    if db_up:
        code = docker_db_up()
        if code != 0:
            return code
        import time

        time.sleep(3)
    if migrate:
        from research_platform.cli_db import cmd_migrate

        code = cmd_migrate()
        if code != 0:
            return code
    if collect:
        from research_platform.collector.mds_collector import MdsCollector

        coll = MdsCollector()
        for sym in ("BTC/USDT", "ETH/USDT"):
            print(coll.ingest_symbol_candles(sym, timeframe="1h", bars=200))
            print(coll.ingest_flows(sym, timeframe="1h"))
    if dq:
        import json

        from engine.config import load_config
        from engine.data import DataLayer
        from research_platform.dq.scanner import scan_ohlcv_frame

        df = DataLayer(load_config()).get_ohlcv_history("BTC/USDT", "1h", bars=200, validate=False)
        print(json.dumps(scan_ohlcv_frame(df, symbol="BTC/USDT", timeframe="1h"), indent=2, default=str))
    print("\nNext: python cli.py research walk-forward --compare --record")
    return 0
