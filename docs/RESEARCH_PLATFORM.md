# Research data platform (MDS v3 implementation)

Phase 1 adds an **optional** PostgreSQL/Timescale database for historical research. The production API continues to use SQLite (`DATABASE_URL`). The deterministic `engine/` path is unchanged.

Production SQLite (verdicts, meta, calibration) has no Alembic — run `python cli.py db init` before first API use, or rely on uvicorn startup (`Database.init()`).

## CLI workflow

```bash
python cli.py research guide          # print all steps
python cli.py research quickstart     # docker up + migrate + collect + dq-scan
python cli.py research setup --enable --db-up --migrate
python cli.py research db status
python cli.py research collect
python cli.py research dq-scan
python cli.py research walk-forward --compare --record
python cli.py research db down
```

### Scheduled automation

When the API runs (`uvicorn api.main:app`), enable research jobs on the same `BackgroundScheduler`:

```bash
export RESEARCH_SCHEDULER_ENABLED=true
export RESEARCH_DB_ENABLED=true   # required for collector persistence
```

| Schedule | Job | Env |
|----------|-----|-----|
| Every N hours | MDS collector | `RESEARCH_COLLECTOR_INTERVAL_HOURS`, `RESEARCH_COLLECTOR_SYMBOLS` |
| Daily (UTC) | Data quality scan | `RESEARCH_DQ_HOUR_UTC` |
| Weekly (UTC) | Walk-forward + artifact record | `RESEARCH_WF_DAY_OF_WEEK`, `RESEARCH_WF_HOUR_UTC` |
| Monthly (UTC) | Production calibration rebuild | `CALIBRATION_DAY_OF_MONTH`, `CALIBRATION_HOUR_UTC` (API settings) |

Manual triggers (same code paths as the scheduler):

```bash
python cli.py research automation-status
python cli.py research run collector
python cli.py research run dq
python cli.py research run walk-forward
```

Dev-only dedicated loop: `python cli.py research scheduler --foreground`

### Internal Research Ops dashboard (web)

Route: **`/research-ops`** in the Next.js app (System → Research ops).

Requires on the **API** host:

```bash
RESEARCH_INTERNAL_API_ENABLED=true
RESEARCH_DB_ENABLED=true   # for MDS sections
```

Single snapshot: `GET /internal/research/v1/dashboard` — scheduler next runs, collector watermarks, DQ reports, dataset versions, storage/Timescale size, walk-forward runs, calibration status, promotion queue (Approve / Defer / Reject), experiment history, activity log.

Manual promotion: `POST /internal/research/v1/promotion-queue/{run_id}/decide` — records decision only; never auto-deploys engine config.

**Promotion:** schedulers never apply config promotion. Walk-forward runs record artifacts only; humans approve promotion per `Research_Roadmap.md`.

Legacy manual env (if not using `--enable`):

```bash
export RESEARCH_DB_ENABLED=true
export RESEARCH_DATABASE_URL=postgresql+psycopg://downpour:downpour@localhost:5433/downpour_research
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
| `research db migrate` | 1 | Alembic upgrade head (`--enable` optional) |
| `research db update` | 1 | `--db-up` + migrate + status (post–git pull) |
| `research db current` | 1 | Alembic revision |
| `research db status` | 1 | Connectivity |
| `research collect` | 5 | Ingest OHLCV + flows into MDS |
| `research dq-scan` | 4 | OHLCV quality report (stdout) |
| `research walk-forward --record` | 8 | WF + `research/artifacts/<uuid>/manifest.json` |
| `research automation-status` | — | Last run metadata + promotion policy |
| `research run collector\|dq\|walk-forward` | — | Manual one-shot (same as scheduler jobs) |
| `research scheduler --foreground` | — | Dev-only blocking APScheduler loop |

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
| `research_platform/jobs.py` | Scheduled collector, DQ, WF (no promotion) |
| `research_platform/promotion_guard.py` | Blocks scheduler-driven promotion |
| `research_platform/scheduler_service.py` | Optional foreground scheduler |

See `docs/HISTORICAL_DATA_ARCHITECTURE.md` for the full blueprint.

## Optional offline DuckDB

```bash
pip install duckdb
```

Use only via `research_platform.cold.storage.duckdb_query_parquet` — not production.
