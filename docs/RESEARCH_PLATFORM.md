# Research data platform (MDS v3 implementation)

Phase 1 adds an **optional** PostgreSQL/Timescale database for historical research. The production API continues to use SQLite (`DATABASE_URL`). The deterministic `engine/` path is unchanged.

## Enable locally

```bash
docker compose -f deploy/research/docker-compose.yml up -d
export RESEARCH_DB_ENABLED=true
export RESEARCH_DATABASE_URL=postgresql+psycopg://downpour:downpour@localhost:5433/downpour_research
pip install -r requirements.txt
python cli.py research db migrate
python cli.py research db status
```

Optional internal dashboard APIs (returns 404 when disabled):

```bash
export RESEARCH_INTERNAL_API_ENABLED=true
uvicorn api.main:app --reload
# GET /internal/research/v1/summary
```

## CLI

| Command | Phase | Description |
|---------|-------|-------------|
| `research db migrate` | 1 | Alembic migrations |
| `research db status` | 1 | Connectivity |
| `research collect` | 5 | Ingest OHLCV + flows into MDS |
| `research dq-scan` | 4 | OHLCV quality report (stdout) |
| `research walk-forward --record` | 8 | WF + `research/artifacts/<uuid>/manifest.json` |

## Migrations

| Revision | Content |
|----------|---------|
| `0001_research_foundation` | Meta + Timescale extension |
| `0002_mds_core` | Candles, flows, registry tables |
| `0003_research_governance` | Dataset versions, experiments, DQ, feature store, jobs |

## Architecture map

| Module | Role |
|--------|------|
| `research_platform/repository/market_data.py` | `live()` → DataLayer; `history()` → MDS with fallback |
| `research_platform/collector/` | Incremental ingest |
| `research_platform/dq/` | Quality reports (no auto-repair) |
| `research_platform/feature_store/` | Versioned cache registry |
| `research_platform/experiments/registry.py` | Reproducibility bundles |
| `research_platform/cold/storage.py` | Parquet + optional DuckDB |
| `api/routes/internal_research.py` | Internal read APIs |

See `docs/HISTORICAL_DATA_ARCHITECTURE.md` for the full blueprint.

## Optional offline DuckDB

```bash
pip install duckdb
```

Use only via `research_platform.cold.storage.duckdb_query_parquet` — not production.
