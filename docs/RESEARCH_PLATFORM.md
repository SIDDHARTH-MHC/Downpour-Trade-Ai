# Research data platform (MDS)

Phase 1 adds an **optional** PostgreSQL/Timescale database for historical research. The production API continues to use SQLite (`DATABASE_URL`).

## Local TimescaleDB

```bash
docker compose -f deploy/research/docker-compose.yml up -d
cp .env.research.example .env   # merge RESEARCH_* vars into your .env
export RESEARCH_DB_ENABLED=true
export RESEARCH_DATABASE_URL=postgresql+psycopg://downpour:downpour@localhost:5433/downpour_research
pip install -r requirements.txt
python cli.py research db migrate
python cli.py research db status
```

## Migrations

Alembic lives under `research_platform/migrations/`. Downgrade is supported for the foundation migration (drops `research_platform_meta` only).

## Architecture

See `docs/HISTORICAL_DATA_ARCHITECTURE.md` (v3). Phase 1 delivers config, engine, migrations, and `ResearchRepository` — no engine or MDS table ingestion yet.
