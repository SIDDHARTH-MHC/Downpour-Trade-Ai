# Infrastructure scale path

Current production uses **SQLite** (`DATABASE_URL=sqlite:///./data/downpour.db`) and **in-process TTL caches** (`api/cache.py`). That is appropriate for a single API container and moderate scan load.

## When to upgrade

Plan **PostgreSQL + Redis** when any of these appear:

- More than **one** API replica behind a load balancer
- Scan or calibration jobs causing **SQLite lock** errors or long write queues
- Need durable **shared** verdict cache across instances
- Outcome / alert workers running separately from the web process

## Target architecture

```
                    ┌─────────────┐
  Vercel (web) ───► │  API (×N)   │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
         PostgreSQL     Redis      Binance (CCXT)
         (verdicts,     (verdict
          outcomes,      cache,
          calibration)   scan lock)
```

## Migration checklist (future)

1. **PostgreSQL**
   - Replace `sqlite3` in `api/db.py` with SQLAlchemy or `psycopg` + parameterized queries.
   - Add indexes: `verdicts(symbol, created_at)`, `outcomes(verdict_id)`.
   - One-time export: `sqlite3 .dump` → import or dual-write period.

2. **Redis**
   - Move `cached_verdict` / scan mutex to Redis keys with TTL.
   - Optional: pub/sub for scan-complete events to webhooks.

3. **Docker Compose**
   - Add `postgres` and `redis` services to `deploy/hetzner/docker-compose.yml`.
   - Env: `DATABASE_URL=postgresql://...`, `REDIS_URL=redis://redis:6379/0`.

4. **No engine changes**
   - `engine/` stays stateless; only `api/` persistence layer changes.

## Interim mitigations (SQLite)

- Keep `scan_workers` modest (`api/settings.py`).
- Batch scan writes (future): single transaction per scan completion.
- Monitor `/health` → `database` and scan duration on `/status`.

Until migration, **do not run multiple write-heavy API processes** against the same SQLite file.
