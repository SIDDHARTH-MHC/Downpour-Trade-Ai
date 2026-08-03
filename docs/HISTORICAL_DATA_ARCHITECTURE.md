# Historical Data Storage Architecture (Research MDS)

**Status:** Final blueprint v3 — **no implementation** until executive sign-off.  
**Date:** 2026-08-04 (rev. 3 — Chief Architect review)  
**Scope:** Research data platform for 10+ years — **does not** modify runtime engine, lanes, synthesizer, or calibration logic.  
**Prerequisites:** `docs/BACKTEST_FIDELITY.md`, `Research_Roadmap.md`, `docs/INFRASTRUCTURE_SCALE.md`, `Quant_Architecture_Blueprint.md`, `.cursor/rules/engine-promotion-gate.mdc`

---

## 0. Design principles (non-negotiable)

| Principle | Implication |
|-----------|-------------|
| **Deterministic engine unchanged** | `engine/` remains pure functions; MDS feeds **inputs**, never verdict logic. |
| **No AI in trading decisions** | MDS holds facts and experiment artifacts — not LLM scores in lanes. |
| **Raw market data is canonical** | All derived layers (features, regime cache, repairs) are **subordinate** and **versioned**. |
| **Feature Store ≠ source of truth** | See **§8** — acceleration and audit only. |
| **Immutable dataset versions** | Benchmarks reference **Dataset Vn**, not rolling “whatever is in the DB today.” |
| **Reproducibility is schema** | Every run binds: `dataset_version_id`, `config_hash`, `engine_git_sha`, `universe_hash`, `feature_manifest_hash`. |
| **Separate planes** | OLTP (product + research registry) · MDS hot (Timescale) · Cold (Parquet) · Compute (replay/feature jobs). |
| **Quality before quantity** | Ingest without **§10** data quality gates is forbidden for frozen datasets. |

**Explicit non-goals:** Replacing lanes/synthesizer/calibration; live API dependence on Feature Store; tick/L2 archives; AI feature discovery inside the engine.

---

## 1. What to store permanently?

*(Rev. 2 content retained — summary below; detail unchanged in spirit.)*

| Class | Must Store (T1) | Nice to Store | Don't Store |
|-------|-----------------|---------------|-------------|
| **Bars** | 1h, 4h, 1d OHLCV | 5m/1m (TTL) | L2, ticks |
| **Flows** | Funding, OI, L/S 1h | Taker ratio, liq agg | — |
| **Macro** | DXY daily | VIX, F&G, calendar | — |
| **Registry** | Dataset versions, experiments, promotions, DQ reports, exchange events | Regime cache, sparse features | — |

**HTF (§1.6 rev. 2):** T1 stores **1h + 4h + 1d** exchange klines; `candle_source` required.

**Universe tiers:** T1 (20–30) full series; T2 (~70) 1h 2–3y; T3 on-demand only.

---

## 2. End-to-end research pipeline (target state)

Institutional platforms separate **definitions** (engine code), **inputs** (MDS), **derived features** (optional store), and **artifacts** (experiments).

```
                         ┌─────────────────────────────────────┐
                         │  OLTP: dataset_versions (frozen)    │
                         │  experiments, promotions, DQ, events  │
                         └──────────────────┬──────────────────┘
                                            │ pins
┌──────────────┐    ┌──────────────┐    ┌───▼──────────────┐    ┌─────────────┐
│ Exchange /   │───►│ MDS canonical │───►│ Replay / Feature  │───►│ engine/*    │
│ Stooq / etc. │    │ (Timescale +  │    │ materialization   │    │ (lanes →    │
│              │    │  Parquet cold)│    │ (§8, optional)    │    │ synthesizer)│
└──────────────┘    └──────────────┘    └───────────────────┘    └──────┬──────┘
                                                                        │
                    ┌───────────────────────────────────────────────────┘
                    ▼
            Verdict (research replay only)
                    │
                    ▼
         experiment_run artifacts (Parquet)
                    │
                    ▼
         promotion_records + attribution (§13)
```

**Live production path (unchanged):** `DataLayer (CCXT) → engine → verdict` — **no Feature Store read** on `/analyze` or scan.

---

## 3. Market regime materialization

*(Rev. 2 §3 — unchanged core decision.)*

- **Production truth:** `engine/lanes/regime.py` at runtime only.  
- **Layer A:** `macro_daily` raw series.  
- **Layer B:** Optional `regime_materialization` with `regime_definition_id`.  
- **Layer C:** Per-experiment `regime_join.parquet`.  

Regime tables are **Feature Store–class derived data** (§8.4), never canonical.

---

## 4. Symbol metadata

*(Rev. 2 §4 — versioned `symbol_metadata` + overrides; sector tags research-only.)*

Experiments on frozen **Dataset Vn** must pin **`metadata_as_of_date`** or **`metadata_hash`** in the run manifest.

---

## 5. Dataset versioning (immutable Dataset Vn)

Rolling `dataset_hash` alone is necessary but **insufficient** for multi-year science. Teams need **named, immutable snapshots** — analogous to benchmark datasets at quant shops (“2019–2024 Binance T1 v3”).

### 5.1 Concepts

| Term | Meaning |
|------|---------|
| **MDS live** | Continuously updated Timescale + rolling Parquet exports. |
| **Dataset Version (Vn)** | **Frozen** manifest + content addressing of all bytes in scope. **Never mutated** after `frozen`. |
| **dataset_hash** | SHA-256 of canonical manifest at a point in time. |
| **dataset_version_id** | Human id e.g. `DS-2026-001` + UUID. |

**Rule:** Published experiments reference **`dataset_version_id`**. Ad-hoc research may use `dataset_hash` on live MDS with a **warning** label — not promotion-eligible.

### 5.2 Schema

```sql
CREATE TABLE dataset_versions (
  id UUID PRIMARY KEY,
  version_code TEXT NOT NULL UNIQUE,     -- 'DS-2026-001', 'CORE-5Y-V1'
  title TEXT NOT NULL,
  description TEXT,

  status TEXT NOT NULL,                  -- draft|validating|frozen|deprecated|archived
  exchange_id TEXT NOT NULL,

  -- Temporal bounds (inclusive bar timestamps, UTC)
  period_start TIMESTAMPTZ NOT NULL,
  period_end TIMESTAMPTZ NOT NULL,

  -- Scope
  tier TEXT NOT NULL,                    -- T1|T2|custom
  symbols TEXT[] NOT NULL,               -- frozen list at validation time
  universe_hash TEXT NOT NULL,
  timeframes TEXT[] NOT NULL,            -- ['1h','4h','1d']
  series_included TEXT[] NOT NULL,       -- candles,funding,oi,long_short,macro_daily,...

  -- Integrity
  dataset_hash TEXT NOT NULL,
  dataset_manifest JSONB NOT NULL,       -- full manifest snapshot at freeze
  parquet_snapshot_uri TEXT,             -- optional immutable cold bundle
  timescale_snapshot_id TEXT,            -- optional pg dump / chunk refs

  -- Quality gate
  data_quality_report_id UUID,           -- FK data_quality_reports
  validation_passed BOOLEAN NOT NULL DEFAULT FALSE,
  validated_at TIMESTAMPTZ,
  validated_by TEXT,

  -- Lineage
  parent_version_id UUID REFERENCES dataset_versions(id),  -- e.g. repair supersedes
  supersedes_reason TEXT,

  created_by TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  frozen_at TIMESTAMPTZ,
  deprecated_at TIMESTAMPTZ,
  archive_uri TEXT
);

CREATE INDEX idx_dataset_versions_status ON dataset_versions(status);
CREATE INDEX idx_dataset_versions_hash ON dataset_versions(dataset_hash);
```

**Example (conceptual):**

| version_code | symbols | period | status |
|--------------|---------|--------|--------|
| CORE-5Y-V1 | BTC, ETH, SOL (+ T1 list) | 2021-01-01 → 2025-12-31 | frozen |

### 5.3 Lifecycle

```
draft → validating → frozen → deprecated → archived
         │              │
         │              └── IMMUTABLE: no row updates except status/metadata labels
         └── DQ jobs (§10), manifest generation, optional Parquet bundle build
```

| Transition | Who | Requirements |
|------------|-----|----------------|
| **draft → validating** | Research ops | Manifest complete; symbols list locked |
| **validating → frozen** | Research lead + automated DQ | `validation_passed=true`; zero **blocking** DQ issues; checksums recorded |
| **frozen → deprecated** | Research lead | Superseded by new Vn; old runs remain valid references |
| **Repair needed** | Never patch frozen | Create **new** `dataset_version` with `parent_version_id`; document in `exchange_events` / `data_repairs` |

### 5.4 Promotion process (research governance)

1. **Promotion gate experiments** (`Research_Roadmap.md`) must use a **`dataset_version_id` with status=frozen`**.  
2. **B0 benchmarks** on `main` should re-run on **latest frozen CORE-* version** monthly — new run id, same dataset version until next freeze.  
3. **New freeze** when: (a) calendar roll (e.g. annual CORE-5Y-V2), (b) material backfill, (c) approved repair lineage.  
4. **`dataset_hash` in live MDS** may drift daily; only **frozen** versions define organizational truth for comparisons.

### 5.5 Archive strategy

| Status | Storage |
|--------|---------|
| **frozen (active)** | Timescale hot and/or Parquet on SSD/object store |
| **deprecated** | Parquet + manifest only; drop from Timescale hot after 90d |
| **archived** | Object storage (Glacier-class); manifest + checksum in Postgres always |

**Parquet bundle at freeze:** Single immutable prefix  
`/datasets/v1/<version_code>/manifest.json` + hive-partitioned copies or **content-addressed** files (`sha256/<hash>.parquet`).

### 5.6 Experiment binding (update to rev. 2 schema)

```sql
-- experiment_runs additions:
  dataset_version_id UUID REFERENCES dataset_versions(id),  -- REQUIRED for promotion-eligible runs
  dataset_hash TEXT NOT NULL,                              -- must match version at freeze
  -- ... engine_git_sha, config_hash, universe_hash, feature_manifest_hash ...
```

---

## 6. Research reproducibility bundle

*(Extends rev. 2 §5 — hash definitions retained.)*

| Hash / ID | Role |
|-----------|------|
| **dataset_version_id** | Organizational freeze pointer |
| **dataset_hash** | Byte-level integrity |
| **config_hash** | `engine/config_hash.py` |
| **engine_git_sha** | Code definition |
| **universe_hash** | Symbol list |
| **feature_manifest_hash** | Degraded-mode declaration |
| **feature_set_id** | Feature Store definition (§8.3) when materialized features used |

**FeatureManifest** (required) — unchanged from rev. 2.

**experiment_runs**, **artifacts/** layout — unchanged; manifest must include **`dataset_version_id`**.

**Re-run policy:** Any change to frozen dataset → **new dataset version**, not reuse of run id.

---

## 7. Promotion history & engine releases

*(Rev. 2 §6 — `engine_releases`, `promotion_records` retained.)*

Add optional FK: `promotion_records.dataset_version_id` — which frozen data justified the promotion.

---

## 8. Research Feature Store

### 8.1 Chief Architect verdict

**Introduce a Research Feature Store — but it must never become canonical.**

Bloomberg/Jump/Two Sigma pattern: **vendor bars are truth**; features are **compiled views** with version stamps. When views disagree with truth, **truth wins** and views are rebuilt.

Downpour equivalent:

| Layer | Canonical? | Role |
|-------|------------|------|
| **MDS (candles, flows, macro)** | **Yes** | Source of all inputs |
| **Feature Store** | **No** | Optional materialized **intermediate** values for speed, parity, cross-experiment joins |
| **Lane scores / verdict** | **No** | Always reproducible from MDS + engine + config |

**Reject:** Feature Store feeding live `/analyze` as primary path.  
**Accept:** Feature Store as **research cache** behind `MarketDataRepository.replay()`.

### 8.2 Pipeline comparison

**Current (correct for production):**

```
Raw → Replay Engine (in-process) → Features (indicators) → Lanes → Synthesizer → Verdict
```

**Research (optional acceleration):**

```
Raw (MDS) ──┬──► Replay Engine ──► Lanes ──► Verdict  (always valid path)
            │
            └──► Feature Store (read-through / write-behind materialization)
                      │
                      └──► Replay may skip recompute IF feature_set_id matches
```

**Invariant:** Any verdict used for **promotion** must be reproducible by **full replay without Feature Store** on the same `dataset_version_id` + `engine_git_sha` + `config_hash` (parity check sample).

### 8.3 Versioning model

Every stored feature row or blob is keyed by:

```
feature_set_id = SHA256(
  engine_git_sha,
  config_hash,
  feature_manifest_hash,
  feature_catalog_version,
  dataset_version_id OR dataset_hash
)
```

**feature_catalog_version:** Declarative list of computed columns (e.g. `ema_20_1h`, `atr_pct_1h`, `regime_label_1h`) — bump when formulas change even if engine repo tag unchanged.

### 8.4 What to materialize vs always recompute

| Feature class | Materialize? | Rationale |
|---------------|--------------|-----------|
| **OHLCV, funding, OI, L/S** | **Never** (MDS only) | Canonical |
| **Indicators (EMA, RSI, MACD, ADX, ATR)** | **Optional** | Cheap to recompute; materialize only for **100M+ bar** batch grids |
| **Structure levels / sweeps / FVG** | **Recompute** default | Depends on config flags; stale risk high |
| **Flow sub-scores (z-scores)** | **Recompute** default | Tied to rolling windows + config thresholds |
| **Regime label** | **Optional cache** (Layer B) | Same as §3; versioned by `regime_definition_id` |
| **Lane scores** | **Sparse only** | At trade bars + parity samples — not every bar |
| **Synthesizer score / verdict** | **Experiment artifacts only** | `oos_trades.parquet` — not a global feature table |
| **Attribution breakdown** | **On promotion** (§13) | Summary stats, not per-bar store |

**Default CX23 policy:** **No Feature Store on day one.** Enable when WF runtime exceeds SLA or DuckDB grid needs pre-joined indicators.

### 8.5 Storage shapes

**Option A — Wide hypertable `feature_values` (narrow use):**

```sql
-- feature_values (hypertable) — USE SPARINGLY
-- ts, exchange_id, symbol, timeframe,
-- feature_set_id, feature_name, value DOUBLE PRECISION,
-- PRIMARY KEY (symbol, timeframe, ts, feature_set_id, feature_name)
```

**Option B — Parquet per (dataset_version, feature_set_id, symbol)** — preferred at scale.

**Option C — On-demand LRU cache (Redis/file)** — no persistence; dev only.

**Recommendation:** Start with **Option C → B**; avoid Option A except T1 indicator packs for DuckDB joins.

### 8.6 Cache semantics

| Question | Answer |
|----------|--------|
| Materialized? | **Yes**, when `feature_set_id` matches and `build_policy=materialized` |
| Cached? | **Yes**, with TTL invalidation on new `feature_set_id` or dataset version |
| Versioned? | **Mandatory** — no unversioned feature reads |
| Invalidation | New engine SHA, config_hash, dataset_version, or catalog bump → **new namespace**; old data retained for old experiments |

### 8.7 Feature Store service boundary (future component)

```
feature_store/
  build.py      -- batch materialize from MDS + engine indicator funcs ONLY (no synthesizer)
  validate.py   -- parity sample vs full replay
  catalog.yaml  -- allowed feature names + dependencies
```

**Catalog rule:** Feature Store may call **`engine/indicators.py`** and shared math — **not** `synthesizer.py` or lane scoring that embeds policy decisions (those stay in replay).

---

## 9. Data quality framework

Research fails silently when candles drop, duplicates appear, or API formats shift. **DQ is a gate for `frozen` dataset versions**, not an afterthought.

### 9.1 Objectives

1. **Detect** anomalies automatically per `(exchange, symbol, series, timeframe)`.  
2. **Block** freeze promotion when severity = blocking.  
3. **Repair** with **audit trail** — never silent overwrite of frozen data.  
4. **Explain** anomalies via **`exchange_events`** (§11).

### 9.2 Schema

```sql
CREATE TABLE data_quality_reports (
  id UUID PRIMARY KEY,
  scope TEXT NOT NULL,                   -- 'symbol_series'|'dataset_version'|'exchange'
  exchange_id TEXT,
  symbol TEXT,
  series TEXT NOT NULL,                  -- 'candles_1h','funding',...
  timeframe TEXT,
  dataset_version_id UUID REFERENCES dataset_versions(id),
  period_start TIMESTAMPTZ,
  period_end TIMESTAMPTZ,

  run_at TIMESTAMPTZ NOT NULL,
  runner_version TEXT NOT NULL,

  -- Aggregates
  expected_bars BIGINT,
  actual_bars BIGINT,
  missing_bars INT NOT NULL DEFAULT 0,
  duplicate_bars INT NOT NULL DEFAULT 0,
  gap_count INT NOT NULL DEFAULT 0,
  corrupt_rows INT NOT NULL DEFAULT 0,
  out_of_order_ts INT NOT NULL DEFAULT 0,

  checksum TEXT,                         -- chunk or range hash
  details JSONB NOT NULL,                -- gap ranges, worst issues

  severity TEXT NOT NULL,                -- ok|warning|blocking
  status TEXT NOT NULL,                  -- open|acknowledged|resolved|wont_fix

  PRIMARY KEY (id)
);

CREATE TABLE data_quality_issues (
  id UUID PRIMARY KEY,
  report_id UUID NOT NULL REFERENCES data_quality_reports(id),
  issue_type TEXT NOT NULL,              -- missing_bar|duplicate|ohlc_invalid|volume_null|timestamp_gap|api_shift|join_break
  ts_start TIMESTAMPTZ,
  ts_end TIMESTAMPTZ,
  detail JSONB,
  severity TEXT NOT NULL
);

CREATE TABLE data_repairs (
  id UUID PRIMARY KEY,
  exchange_id TEXT NOT NULL,
  symbol TEXT NOT NULL,
  series TEXT NOT NULL,
  timeframe TEXT,

  issue_id UUID REFERENCES data_quality_issues(id),
  repair_kind TEXT NOT NULL,             -- backfill|delete_duplicate|interpolate_forbidden|manual_override
  -- interpolate_forbidden: default policy — gaps remain null; engine handles missing

  prior_dataset_hash TEXT,
  new_dataset_version_id UUID REFERENCES dataset_versions(id),

  reason TEXT NOT NULL,
  approved_by TEXT NOT NULL,
  approved_at TIMESTAMPTZ NOT NULL,
  applied_at TIMESTAMPTZ,

  -- Never UPDATE candles in place for frozen sets; repairs create new Dataset Vn
  patch_manifest JSONB
);
```

**Operational view (`data_quality` summary):** Materialized view or nightly rollup joining latest report per `(exchange, symbol, series)` for dashboard (§14).

### 9.3 Detection rules (automated)

| Check | Method | Severity |
|-------|--------|----------|
| **Missing candles** | Expected regular grid from `period_start/end` + timeframe; anti-join on `ts` | blocking if >0.1% bars missing in T1 freeze window |
| **Duplicate timestamps** | `COUNT(*) GROUP BY ts HAVING count>1` | blocking |
| **Corrupt OHLC** | `high >= max(o,c,l)`, `low <= min(o,c,h)`, non-positive prices | blocking |
| **Volume anomalies** | null volume, negative | warning unless sustained |
| **Timestamp gaps** | `ts - lag(ts) > 1.5 * interval` | warning; blocking if exchange claimed continuous |
| **API inconsistencies** | Compare row count vs exchange klines endpoint spot check | warning |
| **Funding/OI alignment** | Orphan funding ts without nearby 1h bar | warning |
| **Cross-series checksum** | Hash of `(ts, close, volume)` stream vs prior freeze | drift detection |

**Runner cadence:** Incremental after each ingest batch; **full scan** before `dataset_versions.validating → frozen`.

### 9.4 Repair policy

| Situation | Action |
|-----------|--------|
| Missing bars | **Backfill** from exchange API; if unavailable, mark gap in manifest — **no synthetic OHLC** |
| Duplicates | Delete duplicate rows in **draft** MDS only; re-hash; new dataset version if already frozen |
| Corrupt row | Delete or re-fetch; log in `data_repairs` |
| Frozen dataset bug | **New dataset version** + deprecate old; re-run affected experiments optionally |

**Repaired data versioning:** Repairs **always** produce new `dataset_hash` and preferably new **`dataset_version_id`**. Never mutate frozen Parquet.

---

## 10. Exchange events

Corporate actions in crypto (delists, migrations, contract changes) explain backtest anomalies and survivorship bias.

### 10.1 Schema

```sql
CREATE TABLE exchange_events (
  id UUID PRIMARY KEY,
  exchange_id TEXT NOT NULL,

  event_type TEXT NOT NULL,
  /*
    listing|delisting|halt|resume|
    symbol_rename|contract_migration|
    futures_launch|futures_delist|
    margin_rule_change|tick_size_change|
    index_constituent_change|reverse_split|airdrop_ratio
  */

  symbol_from TEXT,
  symbol_to TEXT,
  contract_from TEXT,
  contract_to TEXT,

  effective_at TIMESTAMPTZ NOT NULL,
  announced_at TIMESTAMPTZ,
  source TEXT NOT NULL,                  -- exchange_announcement|manual|coingecko|ingest_detected
  source_url TEXT,
  description TEXT NOT NULL,
  payload JSONB,

  -- Research impact
  affects_backtest BOOLEAN NOT NULL DEFAULT TRUE,
  survivorship_note TEXT,

  created_by TEXT,
  created_at TIMESTAMPTZ NOT NULL,

  UNIQUE (exchange_id, event_type, symbol_from, effective_at)
);

CREATE INDEX idx_exchange_events_symbol ON exchange_events(exchange_id, symbol_from, effective_at);
CREATE INDEX idx_exchange_events_time ON exchange_events(effective_at);
```

### 10.2 Ingest sources

1. **Manual curation** — primary for accuracy at small scale.  
2. **Exchange announcement RSS/API** — semi-automated drafts.  
3. **Ingest detectors** — sudden symbol disappearance, 404 on klines, OI drop to zero → **candidate event** for human review.  
4. **Link to `symbol_metadata`** — update `delisted_at`, `symbol_to` lineage.

### 10.3 Research usage

- Filter backtests: exclude trades across delist windows.  
- Join anomaly reports: “PF drop coincided with `contract_migration`.”  
- Universe construction: T1 list as-of **`effective_at`** for historical simulation.

---

## 11. Feature importance & lane attribution history

### 11.1 Should we store it?

**Yes — as informational promotion artifacts, not as runtime inputs.**

When **Engine v1.7** ships, stakeholders ask *“what drove scores?”* Store a **summary** tied to `engine_release_id` / `promotion_records` — not a live dashboard feeding weights.

### 11.2 What to store

```sql
CREATE TABLE engine_release_attribution (
  id UUID PRIMARY KEY,
  engine_release_id UUID NOT NULL REFERENCES engine_releases(id),
  experiment_run_id UUID REFERENCES experiment_runs(id),
  dataset_version_id UUID REFERENCES dataset_versions(id),

  method TEXT NOT NULL,                  -- 'oos_trade_attribution'|'wf_aggregate'|'scan_sample'
  sample_description TEXT,

  -- Example stored summary (informational)
  lane_contribution_pct JSONB NOT NULL,
  /*
    {
      "technical": 34,
      "flow": 29,
      "structure": 26,
      "regime_gating": 11,
      "notes": "Pct of mean |weighted lane contribution| on OOS trades; not causal."
    }
  */

  attribution_details JSONB,             -- optional per-regime breakdown
  disclaimer TEXT NOT NULL DEFAULT 'Informational only; does not modify synthesizer weights.',

  created_at TIMESTAMPTZ NOT NULL
);
```

### 11.3 How to generate

| Method | Source | Use |
|--------|--------|-----|
| **Primary** | Walk-forward **OOS trades** + stored `attribution` on verdict payload (lane weighted contributions) | Promotion summary |
| **Secondary** | Aggregate mean `abs(lane.score * regime.weight)` at signal bars | Cross-check |
| **Not used** | SHAP/ML feature importance | **Forbidden** in deterministic philosophy |

**Timing:** Generated during **promotion packaging** after WF pass — job reads `experiment_run` artifacts, not live traffic.

### 11.4 Boundaries

- **Does not** change `config.yaml` weights.  
- **Does not** feed calibration.  
- **May** appear in internal Research Dashboard (§14) and release notes.

---

## 12. Internal Research Dashboard (architecture only)

**Audience:** Researchers and research ops — **not** end users. **No UI implementation** in this blueprint — define **read models**, **APIs**, and **data sources**.

### 12.1 Goals

Single pane for **MDS health**, **experiment velocity**, and **production research alignment** (calibration drift, WF status).

### 12.2 Logical architecture

```
┌─────────────────────────────────────────────────────────────┐
│  research-dashboard-api (read-only, internal auth)          │
│  Aggregates from OLTP + MDS metadata — never mutates engine │
└───────────────────────────────┬─────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
  Postgres OLTP            Timescale stats          Object store metrics
  (experiments,            (hypertable sizes,        (Parquet bytes,
   datasets, DQ,             chunk compression)        export lag)
   promotions, queue)
```

**Deployment:** Same Hetzner VM initially (`research.internal` VPN or admin-only route); later isolated read replica.

### 12.3 Module catalog

| Module | Data sources | Key metrics |
|--------|--------------|-------------|
| **Dataset freshness** | `ingest_watermarks`, `dataset_versions` | `last_ts` per series; lag vs wall clock; active `frozen` versions |
| **Backfill status** | Collector job table (future `ingest_jobs`) | % complete, symbols pending, rate-limit pauses |
| **Storage usage** | Timescale `hypertable_size`, disk, Parquet inventory | GB by tier, growth/week, compression ratio |
| **Universe** | `universe_registry`, `symbol_metadata` | Current T1/T2 lists, diffs vs last freeze |
| **Data quality** | `data_quality_reports`, open issues | blocking count, worst symbols, repair queue |
| **Missing symbols** | DQ missing bars + watermarks | Symbols below completeness threshold |
| **Latest experiments** | `experiment_runs` | Last 50 runs, status, variant, PF summary |
| **Promotion history** | `promotion_records`, `engine_releases` | Timeline, decisions, links to EXP markdown |
| **Production config** | `engine_releases` latest + `config_hash` | Diff vs previous release |
| **Calibration drift** | `calibration_versions` vs live bucket win rates | Bucket monotonicity warnings |
| **Walk-forward status** | Last WF job, `experiment_runs.run_kind=walk_forward` | Pass/fail per symbol, OOS trade count |
| **Research queue** | `research_jobs` (future) | Queued/running/backpressure |
| **Storage growth forecast** | Weekly snapshot table | Projected months to disk cap |

### 12.4 Suggested read-only API surface (internal)

Prefix: `/internal/research/v1/` (never exposed on public API).

| Endpoint | Purpose |
|----------|---------|
| `GET /summary` | KPI strip for dashboard home |
| `GET /datasets` | List dataset versions + freshness |
| `GET /datasets/{version_code}` | Manifest + DQ status |
| `GET /quality` | Rollup of open DQ issues |
| `GET /experiments` | Filterable run list |
| `GET /promotions` | Promotion timeline |
| `GET /storage` | Bytes, forecasts |
| `GET /universe` | T1/T2 current vs frozen |
| `GET /calibration/drift` | Bucket stats vs live outcomes |
| `GET /queue` | Research job queue depth |

### 12.5 Auth & multi-researcher

| Concern | Design |
|---------|--------|
| **Identity** | `researchers` table; SSO later |
| **RBAC** | `viewer` \| `researcher` \| `lead` \| `ops` — freeze dataset = lead only |
| **Audit** | All freeze/promote/repair actions logged |
| **Quotas** | Max concurrent WF jobs per researcher on shared CX23 |

---

## 13. Storage estimates & retention

*(Rev. 2 §7, §11 — ~2.35 MB/pair/year for 1h+4h+1d+flows; T1 30×5y ≈ 120–220 MB compressed.)*

**Retention:** Frozen dataset versions **immutable**; deprecated → Parquet archive; see §5.5.

---

## 14. Database planes (consolidated)

```
┌─────────────────────────────────────────────────────────────────┐
│  PostgreSQL OLTP                                                 │
│  dataset_versions, experiments, experiment_runs, promotions      │
│  data_quality_*, data_repairs, exchange_events, symbol_metadata  │
│  engine_releases, engine_release_attribution, researchers        │
│  verdicts, outcomes, calibration_versions (product)                │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  TimescaleDB MDS (hot)                                           │
│  candles, funding, open_interest, long_short_ratio, macro_daily  │
│  optional: feature_values (narrow), regime_materialization       │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  Parquet cold + DuckDB (offline research)                        │
│  frozen dataset bundles, T2 bulk, experiment artifacts           │
└─────────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────────┐
│  Feature Store (derived, versioned) — §8                         │
│  Parquet/feature cache; NOT canonical                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 15. DuckDB + Parquet (offline research)

*(Rev. 2 §10 — unchanged triggers and workload split.)*

**Addition:** Frozen **`dataset_version`** Parquet bundles are the **preferred DuckDB input** for 5–10y studies — single manifest pointer per experiment.

---

## 16. Institutional stress test (10y, 100M+ candles, 1000 pairs, 10 exchanges)

**Scenario:** 10 exchanges · 1,000 pairs · 10 years · ~**876M** 1h bars (order 10^8–10^9) · thousands of researchers · thousands of experiments/day at peak.

### 16.1 Scale math (order of magnitude)

| Asset | Rough size |
|-------|------------|
| 1h candles only (1k pairs × 10y) | ~876M rows × ~100 B ≈ **87 GB** raw → **~10–15 GB** compressed Parquet |
| +4h +1d | +~15% |
| Flows (funding/OI/L-S) | +~30–40 GB raw cold → compress |
| **100M candles** (subset) | Fits easily in cold Parquet; **not** in CX23 Timescale |

### 16.2 What still holds

| Decision | Holds? |
|----------|--------|
| Raw MDS canonical | **Yes** |
| Feature Store non-truth | **Yes** — mandatory at this scale |
| Immutable Dataset Vn | **Yes** — essential for comparability |
| Engine/lanes/synthesizer/calibration unchanged | **Yes** |
| DQ + exchange events | **Yes** — more critical, not less |
| DuckDB for analytical workloads | **Yes** |
| Promotion on frozen datasets only | **Yes** |

### 16.3 What breaks / must evolve

| Component | CX23 today | At full scale |
|-----------|------------|---------------|
| Single Timescale on 40 GB | T1 only | **Hot window only** (~24–36 mo, ~50–100 active pairs) |
| Full recompute WF | 2 vCPU | **Batch cluster** (Hetzner dedicated / spot) — **research workers**, not API |
| `dataset_hash` full scan | OK | **Incremental manifests** + chunk checksums |
| Single collector IP | OK | **Per-exchange worker** + queue (Kafka/NATS or Postgres job queue) |
| SQLite product OLTP | OK | **Postgres** + read replica for dashboard |
| Thousands of experiment rows/day | OK | **Partition** `experiment_runs` by month; metrics in Parquet |
| Multi-researcher | 1–2 | **RBAC**, quotas, shared queue (§12.5) |

### 16.4 Target topology (year 5–10)

```
Exchange adapters (10) → Ingest queue → MDS writers
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
      Timescale (hot)                  Parquet lake (canonical cold)
      T1 recent                        All frozen Dataset Vn
              │                               │
              └───────────┬───────────────────┘
                          ▼
              Research worker pool (replay + optional Feature Store build)
                          ▼
                   engine/* (unchanged code)
                          ▼
              Artifacts → object storage; metadata → Postgres
                          ▼
              Internal Research Dashboard (read replica)
```

**Live API:** Still **CCXT + cache** — **not** querying 876M rows.

### 16.5 Failure modes to design against

1. **Silent data drift** — mitigated by §9 DQ + frozen versions.  
2. **Feature Store skew** — mitigated by parity replay samples before promotion.  
3. **Survivorship bias** — mitigated by §10 exchange events + point-in-time universes.  
4. **Experiment combinatorial explosion** — mitigated by requiring `dataset_version_id` + promotion class limits (`Research_Roadmap.md` one P4 per release).  
5. **Researcher distrust** — mitigated by immutable Vn + public internal promotion timeline.

---

## 17. Engine boundary (unchanged)

```
  Live:     DataLayer (CCXT) ──────────────────────► engine ──► verdict

  Research: MarketDataRepository.history(dataset_version_id)
                 │
                 ├─► [optional Feature Store read-through]
                 └─► engine (identical functions, identical config_hash)
```

Production **never** depends on MDS, Feature Store, or DuckDB availability.

---

## 18. Implementation phases (post sign-off)

| Phase | Deliverable |
|-------|-------------|
| **P0** | Sign §5 Dataset Vn, §8 Feature Store policy, §9 DQ gates |
| **P1** | Timescale + T1 ingest + watermarks |
| **P2** | DQ runner + `data_quality_reports`; blocking rules |
| **P3** | `dataset_versions` freeze workflow + first CORE-* V1 |
| **P4** | `experiment_runs` + mandatory `dataset_version_id` for promotion runs |
| **P5** | `exchange_events` + symbol lineage |
| **P6** | `promotion_records` + `engine_release_attribution` |
| **P7** | Parquet frozen bundles + DuckDB templates |
| **P8** | Feature Store catalog + parity validator (optional) |
| **P9** | Internal Research Dashboard API (§12) |
| **P10** | Multi-exchange collectors + cold lake scale-out |

---

## 19. Open decisions for executive sign-off

1. **First frozen dataset:** `CORE-5Y-V1` symbol list and end date.  
2. **DQ blocking thresholds** for T1 (missing bar %).  
3. **Feature Store:** defer until P8 vs early indicator materialization.  
4. **Repair authority:** single research lead vs two-person rule.  
5. **Dashboard auth:** VPN-only vs OAuth.  
6. **Postgres/Timescale:** single node vs managed split at P1.  
7. **Attribution method:** confirm OOS trade attribution as canonical summary.

---

## 20. References

- `docs/BACKTEST_FIDELITY.md`  
- `Research_Roadmap.md`, `.cursor/rules/engine-promotion-gate.mdc`  
- `docs/INFRASTRUCTURE_SCALE.md`  
- `Quant_Architecture_Blueprint.md`  
- `engine/lanes/regime.py`, `engine/config_hash.py`, `engine/analyzer.py` (live data path)

---

## Appendix A — Rev. 2 sections merged by reference

The following rev. 2 content remains valid and is incorporated by reference above:

- **§1.6** Higher timeframe storage (1h+4h+1d T1).  
- **§3** Regime three-layer model.  
- **§4** Symbol metadata schema.  
- **§6–7** Promotion records schema; storage MB estimates.  
- **§15 DuckDB** workload split and Parquet layout.

---

*This document is the **final production-grade blueprint** for Downpour’s research data platform (MDS + governance + optional Feature Store). It preserves deterministic engine, lane, synthesizer, and calibration philosophy while enabling 10+ years of reproducible quantitative research. **No implementation** until §19 sign-off.*
