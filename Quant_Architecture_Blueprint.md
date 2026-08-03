# Downpour Trade AI — Quant Research & Architecture Validation Blueprint

**Date:** 2026-08-04  
**Audience:** Engineering, quant research, product leadership  
**Prerequisite docs (state of record):** `Implementation Audit Report.md`, `UI_UX_Audit.md`, `Strategy_Review.md`, `Capability_Gap_Analysis.md`, `Competitive Enhancement Plan.md` v2.0, `README.md`, `docs/BACKTEST_FIDELITY.md`, `docs/INFRASTRUCTURE_SCALE.md`

**Instruction honored:** This document **does not re-list** prior audit findings (e.g. bucket unification, outcome bar ordering, WF fail UX, frontend phase letters). It adds **institutional-scale validation**, **quantitative structure**, and **evolution path** assuming the **current lane + synthesizer foundation is retained**.

---

## 1. Executive Summary

**Verdict:** The architecture **can** evolve into a top-tier **deterministic crypto intelligence** platform—analogous to “Bloomberg + internal risk system” for discretionary/systematic crypto desks—not a TradingView indicator clone or an LLM signal shop. The **engine boundary is correct**: stateless `engine/` orchestration, explicit gates, calibration separated from scoring, context firewalled from synthesis.

**What must change for scale (not philosophy):** Split **market-data plane**, **compute plane**, and **persistence plane**; eliminate **SQLite + in-process cache** as the system of record at high QPS; introduce **bar-aligned feature snapshots** for research/production parity; run **offline weight and threshold estimation** under walk-forward constraints instead of growing indicator count.

**What must change for quant quality:** Reduce **effective degrees of freedom** in the technical lane (correlated trend/momentum stack); promote **structure events** and **orthogonal flow** features; move non-reproducible feeds to **Context** permanently unless versioned historical archives exist.

**Final direction confidence:** **High (8/10)** on product wedge (trust + determinism); **Medium (6/10)** on production scale without infra migration; **Medium-high (7/10)** on statistical edge until live/backtest fidelity gap is narrowed.

---

## 2. Architecture Validation

### 2.1 Question: Keep this architecture at 100k users / 10M analyses/day / hundreds of pairs / multi-exchange / multi-asset?

**Keep:** The **logical** architecture:

```
Market data → Feature extraction (lanes) → Regime → Synthesizer → Risk → Verdict
                ↘ Calibration (offline)     ↘ Trust / Replay / Explain (derived)
Context feeds → (no edge into synthesizer)
```

**Do not keep as-is:** The **physical** deployment shape—monolithic API + scheduler + SQLite + per-request CCXT fan-out + threaded scan writing one row at a time.

### 2.2 Institutional reference model (target evolution)

Think **Jane Street / Jump**: research and production share **definitions**, not **processes**.

| Plane | Today | At scale |
|-------|--------|----------|
| **Market data** | CCXT inside `DataLayer` per analyze | Dedicated **MDS**: normalized candles, funding, OI, L2 snapshots; exchange adapters; coalesced subscriptions |
| **Feature / engine** | Sync Python in API workers | **Stateless workers** (horizontal); pure functions of `(symbol, tf, bar_ts, feature_blob)` |
| **Research** | `backtest.py` loop + manual calibrate | **Batch replay grid** on object storage; experiment registry; promoted configs only |
| **Serving** | FastAPI + cachetools | API **read path** + **job queue** for scan/calibrate; Redis verdict cache |
| **Persistence** | SQLite | **PostgreSQL** (verdicts, outcomes, config versions); optional **Timescale** for bars |
| **Observability** | `/health`, basic logs | SLOs on data freshness, bar age, lane skip rates, calibration drift |

### 2.3 Bottlenecks (new framing)

1. **Exchange rate limits & IP reputation** — 10M analyses/day implies **reuse of bar features**, not 10M full `analyze_symbol` cold paths. Without MDS, Binance will throttle before CPU limits.
2. **Coupling analyze ↔ fetch** — `analyzer.py` instantiates `DataLayer` per call; scale requires **injected snapshots** (testability + cache locality).
3. **Write amplification** — Scheduler scan: parallel analyze + **per-symbol DB write** (`Implementation Audit` pattern). At 500 pairs × frequent scans → **OLTP hotspot** even on Postgres without batching.
4. **Calibration as heavyweight cron** — Walk-forward in-process blocks a worker; belongs on **job tier** with artifact output (calibration vN immutable blob).
5. **Multi-exchange** — CCXT abstraction exists mentally but **config + symbol mapping + funding semantics** are Binance-shaped; each exchange is a **new adapter contract**, not a flag.
6. **Multi-asset** — Engine assumes crypto spot/perp semantics; equities/FX need different **session calendar, halts, and flow** — same *lane pattern*, different **feature plugins** behind interfaces.

### 2.4 Scaling risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Live/backtest feature skew | **Critical** for trust | Versioned **FeatureManifest**; WF uses same code path with declared degradations |
| Config drift without versioning | High | Store `config_hash` on every verdict; promote configs like model releases |
| SQLite corruption / lock | High at multi-replica | Postgres + single-writer jobs (`INFRASTRUCTURE_SCALE.md`) |
| Spoofed L2 in live-only features | Medium | Keep wall cap; optional **persistence filter** (time-at-price) in MDS |
| Research overfitting to Binance 2022–2025 | Medium | Multi-symbol, multi-regime WF; holdout exchanges |

### 2.5 Would we keep this architecture?

**Yes—conceptually.** **No—operationally** without MDS + OLAP/OLTP split + async scan pipeline.

**Compelling reason NOT to add a 5th “Macro lane” in monolith:** Macro belongs in **Context service** feeding **Regime modifiers** only when bar-aligned series exist—avoid duplicating synthesizer logic.

---

## 3. Mathematical Review (Quant Quality)

### 3.1 Correlation / double-counting (within technical lane)

Current technical score combines:

- **EMA stack** (trend alignment)
- **EMA200 side** (partially redundant with stack)
- **RSI** (momentum / mean-reversion hybrid)
- **MACD histogram slope** (momentum; MACD **built from EMAs** → correlated with stack)
- **ADX multiplier** (scales **entire** score when trend strength high)

**Institutional read:** This is not “EMA + MACD + Supertrend” literally, but **three trend/momentum views + a global amplifier**—effective **double (triple) counting of directional conviction**, not independent evidence.

**Recommendations (simplification, not new indicators):**

| Change | Rationale | Lane |
|--------|-----------|------|
| Demote **EMA200 side** when stack already scored | Redundant margin | Technical |
| Treat **MACD** as *confirmation* only when stack sign agrees; else evidence-only | Cuts opposing momentum false boosts | Technical |
| Apply **ADX multiplier** to **technical sub-score only**, not after stacking RSI penalties | Prevents ADX from amplifying mean-reversion penalties incorrectly | Technical |
| Cap **absolute technical** contribution before regime weighting | Reduces lane dominance | Synthesizer input |

**Supertrend / Bollinger:** Not present—**do not add**; ADX+EMA already cover trend/chop split.

### 3.2 Cross-lane correlation

- **Structure breakout** and **technical MACD rising** often co-occur → synthesizer **alignment rule** partially intentional, but **lane conflict threshold (80)** is a crude independence test.
- **Flow OI+price** and **technical trend** correlate in bull markets → **regime weights** (trending → technical 1.3) **increase** correlation exposure.

**Recommendation:** Offline **lane correlation matrix** per regime on historical verdicts; if corr(structure, technical) > 0.6 in TRENDING_UP, **lower one weight** in config promotion process—not more indicators.

### 3.3 Weighting statistical justification

Weights in `config.yaml` are **expert priors**, not MLE/MAP estimates. That is acceptable for v1 **if** promotion requires:

1. Walk-forward **OOS profit factor** non-degradation  
2. **Bucket monotonicity** (higher |score| → not worse win rate)  
3. **Stability** across BTC/ETH/SOL holdouts  

**Recommendation:** Introduce **Research tier** that fits **only**:

- Synthesizer thresholds (`long_threshold`, alignment)  
- Regime weight table  
- Bounded structure/flow coefficients  

…via **constrained grid or Bayesian optimization** on **OOS only**. Production config = **signed artifact**, not hand-edited YAML on server.

### 3.4 Evidence vs score vs confidence modifier

| Signal class | Today | Should be |
|--------------|-------|-----------|
| BOS/CHoCH | Evidence (events) | **Evidence** until WF proves incremental OOS |
| Funding z-score | Score | **Score** (orthogonal to price patterns) |
| Book walls | Score (capped) | **Score** live; **evidence-only** in backtest (already degraded) |
| News sentiment | Context | **Never score** |
| WF pass/fail | Dashboard/trust | **Confidence modifier** (label prefix or tier cap) |

**Confidence modifiers** should live in **Trust layer** (`calibrate_label`, `trust_payload`)—not hidden inside lane scores—so backtest buckets remain interpretable.

### 3.5 Regime-specific activation (simplification)

| Feature | RANGING | TRENDING | SHOCK |
|---------|---------|----------|-------|
| Structure proximity | Full | Reduced (already 0.8 wt) | Off |
| Breakout volume | Full | Full | Off |
| RSI penalties | Full | Reduce | Off |
| Flow funding z | Full | Full | Off |

**Recommendation:** Explicit **regime feature mask** in config (boolean toggles per lane submodule)—cleaner than adding indicators.

---

## 4. Data Quality Review

| Dataset | Reliability | Latency | History for backtest | License | Engine use |
|---------|-------------|---------|----------------------|---------|------------|
| Binance spot OHLCV | High | Low | Long | ToS | **Score** |
| Binance USDM funding/OI | High | Low | Medium via CCXT | ToS | **Score** (when aligned) |
| Binance L2 book | Medium (spoof) | Low | **None** intraday archive | ToS | **Score live / absent BT** |
| Binance agg trades (taker) | High | Low | Not stored | ToS | **Score live / absent BT** |
| CoinGecko global | Medium | Medium | Limited | Free tier | **Context** |
| RSS news | Medium | High variance | No stable archive | Publisher ToS | **Context** |
| ETF flows | N/A today | — | — | Paid | **Context** |
| Liquidations | N/A | — | Vendor-dependent | Paid | **Context** until archive |
| On-chain | Vendor | Slow | Yes (paid) | Paid | **Context** default |
| DXY / VIX / yields | Yahoo/FRED | Low | Long | Various | **Regime context** only first |

**Rule enforced:** If it cannot be reproduced on **`df.iloc[:i+1]`** (or equivalent MDS snapshot at `t`), it **must not** enter lane scores in production without a **declared degradation flag** matching backtest.

**Survivorship:** `scan_top` liquidity selection biases to current winners—research should **freeze universe** per calibration run and store symbol list hash.

---

## 5. Lane Ownership Matrix

**Rule:** Exactly one **owner** per capability; others may **consume** outputs read-only.

| Capability | Owner | Consumers (read-only) |
|------------|-------|------------------------|
| EMA/RSI/MACD/ADX | **Technical** | Explainability, Replay, Attribution |
| Swing S/R, VP, walls, breakout | **Structure** | Risk (levels), Events, Replay |
| BOS/CHoCH labels | **Structure** (events submodule) | Replay, UI; not second lane |
| Funding/OI/taker/L-S (future) | **Flow** | Explainability, Flows dashboard |
| SHOCK/COMPRESSION/TREND weights | **Regime** | Synthesizer, Attribution |
| Weighted score & alignment gates | **Synthesizer** | Risk, Calibration input |
| SL/TP/size/R:R gate | **Risk** | Trust, Lifecycle |
| Bucket labels & WF metadata | **Calibration** | Trust |
| WF pass/fail, bucket stats | **Trust** | UI, Coach copy |
| why/why_not/risk text | **Explainability** | Copilot (template), Replay |
| Timeline ordering | **Replay** | UI |
| News/ETF/macro/liq tiles | **Context** | UI, optional Regime **warnings** |
| Scan rejection buckets | **Analytics** (`scan_report`) | Dashboard |

**Conflict resolution:** If “macro shock” ever blocks trades, **Regime** owns the gate; Context supplies **inputs** (time series), not parallel NO_TRADE logic in API routes.

---

## 6. Feature Classification Matrix (Deterministic Expansion)

Classification keys: **(1)** Score Input · **(2)** Confidence Modifier · **(3)** Regime Modifier · **(4)** Context Only · **(5)** Dashboard Only · **(6)** Should Never Be Added

| Feature | Classification | Why (one line) |
|---------|----------------|--------------|
| Liquidity sweep | **(1)** Structure | Rule-based; backtestable on OHLCV |
| Equal highs/lows | **(1)** Structure | Deterministic; improves level quality |
| FVG | **(1)** or evidence-first | OHLCV gap rule; marginal edge—start as evidence |
| VWAP | **(4)** or weak **(1)** | Session definition required; else context |
| Long/short ratio | **(1)** Flow | Exchange API; align history or degrade |
| Liquidations | **(5)** → **(4)** | No history → dashboard; archive → context warnings |
| ETF flows | **(4)** | Licensed; not bar-aligned in MVP |
| On-chain | **(4)** / **(5)** | Slow; desk context, not 1h alpha default |
| Macro (DXY, yields) | **(3)** Regime | Daily series → tradeability flag, not lane score |
| Psychology (F&G) | **(4)** | Index construction opaque; trust risk |
| News NLP/LLM | **(6)** | Breaks determinism & backtest |
| Social sentiment | **(6)** | Manipulation + non-reproducible |
| Options GEX | **(5)** | Data cost; unproven for spot/perp 1h |
| ICT kill zones | **(6)** in score | Subjective time zones |
| Whale wallet labels | **(4)** | Label SLA; never unscored Nansen copy |

---

## 7. Statistical Validation (Future Features — Expected Value)

| Feature | Δ Precision | Δ Recall | Overfit | Calibration | WF | Recommend if weak? |
|---------|-------------|----------|---------|-------------|-----|---------------------|
| Liquidity sweep | + small/medium | − | Medium | Improves if OOS↑ | Must re-run | **Yes** |
| Equal H/L | + small | − small | Low | Neutral | Neutral | **Yes** |
| FVG | + tiny | + tiny | Medium | Unclear | Unclear | **Defer** |
| L/S ratio | + small | ↔ | Low | Improves flow parity | Test | **Yes** |
| VWAP score | ↔ | ↔ | Medium | Harm if session wrong | — | **No** (context) |
| Liquidations score | ? | + | **High** | Harm | ↓ | **No** (dashboard) |
| ETF/on-chain score | ? | + | **High** | Harm | ↓ | **No** |
| Macro regime flag | + selective | − | Low | Honest warnings | ↑ trust | **Yes** (modifier) |
| Demote MACD redundancy | + clarity | − slight | **↓** | ↑ interpretability | ↑ | **Yes** |

**Gate for merge:** Any scored feature must show **non-inferior OOS PF** and **stable bucket monotonicity** on at least two majors over ≥12 months degraded-mode backtest.

---

## 8. Recommended Enhancements (Architecture-Aligned)

**Priority 0 — Platform integrity (quant infra, not features)**

1. **Config + calibration versioning** on every verdict (`config_hash`, `calibration_id`).  
2. **FeatureManifest** documenting live vs backtest degradations (extend `BACKTEST_FIDELITY.md` into machine-readable schema).  
3. **Batch scan writes** + job queue for calibrate/WF.  
4. **MDS prototype**: one process publishes 1h bars + funding/OI snapshots; engine consumes protobuf/parquet.

**Priority 1 — Signal quality (fewer DOF, not more indicators)**

5. Technical lane **orthogonalization** (stack OR MACD confirm; ADX scope fix).  
6. Structure **sweep + equal highs/lows** with evidence + bounded score.  
7. Flow **long/short ratio** with z-score evidence string.

**Priority 2 — Trust & research**

8. Offline **weight/threshold promotion pipeline** (walk-forward constrained).  
9. **Lane correlation report** per regime (internal dashboard).  
10. Trust **confidence modifiers** from WF pass/fail (explicit in label, not hidden).

**Priority 3 — Context depth (no synthesis)**

11. DXY + 10y yield **regime warning** inputs.  
12. Liquidation **dashboard** (vendor, labeled).

---

## 9. Features to Reject (Philosophy Violations)

- LLM or embedding **signal** generation  
- Narrative **score** from news  
- Parallel Strategy Builder executing non-engine rules as “official” signals  
- Footprint/delta without exchange-certified historical feed  
- Indicator catalog expansion (Supertrend, Ichimoku, etc.) without **replacing** existing correlated terms  
- Auto-trade execution inside core product  
- “Confidence 87%” **opaque** scores not tied to bucket `n` and PF  

---

## 10. Long-Term Research Agenda

1. **Production–research parity metric** — max |live_score − replay_score| per lane at same bar.  
2. **Regime-conditioned calibration** — separate buckets by `regime.name` (data permitting).  
3. **Structural alpha decay** — wall persistence half-life; cap dynamics from data.  
4. **Cross-exchange arbitrage of signal** — same engine, different MDS feeds; meta-NO_TRADE when exchanges disagree.  
5. **Portfolio-level risk** — correlation-aware sizing (engine extension of `portfolio_analytics`, not new lane).  
6. **Adversarial book detection** — simple cancel-rate proxies when trade data available.  
7. **Causal hooks** — event study around **exchange RSS** maintenance (deterministic event windows).

---

## 11. Five-Year Product Roadmap (Unlimited Engineering)

Focus: **most trusted deterministic crypto intelligence**, not widest indicator set.

### Version 2 — “Parity & Proof” (months 0–12)

| Dimension | Deliverables |
|-----------|--------------|
| **Capabilities** | Sweep/equal levels; L/S ratio; technical simplification; trust modifiers from WF |
| **Infrastructure** | Postgres + Redis; scan/calibrate jobs; config/cal artifacts |
| **Data** | MDS v1 (Binance); snapshot store for L2 samples (optional) |
| **Research** | Automated promotion pipeline; lane correlation reports |
| **UX** | Projection layer (bias, trend strength) from JSON; calibration drift UI |
| **AI assistance** | Explain-only copilot; **no signal change** |
| **Analytics** | Feature parity dashboard; scan rejection trends |

### Version 3 — “Multi-venue & Desk Grade” (years 1–2)

| Dimension | Deliverables |
|-----------|--------------|
| **Capabilities** | Regime masks; macro **warning** inputs; portfolio risk caps |
| **Infrastructure** | Horizontal engine workers; read replicas; rate-limit budgeter |
| **Data** | Second exchange adapter; historical L2 archive policy |
| **Research** | Regime-specific buckets; cross-exchange holdouts |
| **UX** | Compare signals; watchlist alerts; API keys for institutions |
| **AI assistance** | NL **query → SQL/JSON path** on verdict store (read-only) |
| **Analytics** | Client-facing **Trust API** (SLA on data freshness) |

### Version 4 — “Intelligence Network” (years 2–4)

| Dimension | Deliverables |
|-----------|--------------|
| **Capabilities** | Context **feeds → Regime only** where bar-aligned; liquidation context warnings |
| **Infrastructure** | Timescale/feature store; global CDN for read API |
| **Data** | Licensed ETF/on-chain **context** with immutable daily snapshots |
| **Research** | Online drift detection on bucket win rates; auto-schedule recalibrate |
| **UX** | Embedded widgets; white-label terminal modules |
| **AI assistance** | Research copilot on **experiment registry** (not live trades) |
| **Analytics** | Attribution of P&L vs engine version (for paper partners) |

### Version 5 — “Reference Standard” (years 4–5)

| Dimension | Deliverables |
|-----------|--------------|
| **Capabilities** | Multi-asset plugins (FX/equity hours) sharing lane interfaces |
| **Infrastructure** | Multi-region active-active read; single-writer calibration region |
| **Data** | Unified MDS for spot/perp/options **context** |
| **Research** | Published methodology docs + third-party replication package |
| **UX** | Industry benchmark: “WF-pass rate” and bucket cards as norm |
| **AI assistance** | Strictly separated **R&D LLM** environment—zero prod path |
| **Analytics** | Public ** transparency reports** (scan rates, NO_TRADE reasons, data outages) |

---

## 12. Engine Philosophy — Non-Negotiables

| Principle | Status in codebase | Threats to watch |
|-----------|-------------------|------------------|
| Deterministic | ✅ Same inputs → same verdict | Hidden LLM, random tie-break |
| Explainable | ✅ evidence[] + explanation | Opaque numeric confidence |
| Backtestable | ✅ Bar loop | Scoring unreproducible feeds |
| Walk-forward validated | ✅ `run_walk_forward` | Skipping WF on config promote |
| Calibrated | ✅ Buckets | Live/backtest skew |
| Reproducible | 🟡 Config not versioned on verdict | Ops drift |
| NO_TRADE valid | ✅ Synthesizer default | Product pressure to “always signal” |
| AI never generates signals | ✅ Coach/copilot | “Hybrid AI synthesizer” requests |

Any proposal failing this table → **reject** regardless of competitor parity.

---

## 13. Final Architecture Score

| Criterion | Score (1–10) | Comment |
|-----------|--------------|---------|
| Logical separation (engine/api/web) | **9** | Clean; keep engine stateless |
| Quant rigor (independence, DOF) | **6** | Correlated technical stack; priors not fitted |
| Research/production parity | **5** | Documented skew; fix via MDS + manifest |
| Scalability (10M/day) | **4** | Needs MDS + queue + Postgres |
| Trust & calibration design | **8** | WF + buckets; versioning gap |
| Context firewall | **9** | Explicit in news module |
| Multi-exchange readiness | **5** | Binance-centric |
| Institutional UX of proof | **7** | Strong API; needs parity metrics |

**Composite architecture score: 6.6 / 10** — **strong foundation**, **not yet scale-ready**, **quant simplification overdue**.

---

## 14. Final Confidence in Current Direction

| Statement | Confidence |
|-----------|------------|
| Deterministic lane + synthesizer is the right **moat** vs AI signal apps | **Very high** |
| Current feature set is ** sufficient** for v1 product | **High** |
| Adding indicators is the wrong next lever | **Very high** |
| Infra migration is **necessary** before 100k DAU aggressive scans | **High** |
| Structure/flow parity in backtest is **necessary** before marketing “provable” at scale | **Very high** |
| Five-year vision as **trusted intelligence standard** is achievable without LLM signals | **High** |

**Net:** **Proceed** on current philosophy; **invest next** in data plane, parity, and statistical simplification—not competitor feature checklists.

---

*End of blueprint. No code was modified.*
