# Downpour Trade AI — Research Roadmap

**Date:** 2026-08-04  
**Status:** Frozen architecture — **no synthesizer changes without completing an experiment in this playbook.**  
**Companion:** `.cursor/rules/engine-promotion-gate.mdc`, `Quant_Architecture_Blueprint.md`, `docs/BACKTEST_FIDELITY.md`

---

## 1. Purpose

Institutional teams do not ship ideas. They ship **promoted artifacts** after:

```
Hypothesis → Experiment → Walk-forward → Calibration impact → Production config
```

This document defines **what to run**, **how to decide**, and **where winners integrate**—without adding features by default.

**Default outcome of every experiment:** **Reject** or **Context/Evidence only** until OOS criteria pass.

---

## 2. Global experiment protocol

### 2.1 Universes & horizons

| Tier | Symbols | Timeframes | History (min) | Notes |
|------|---------|------------|---------------|--------|
| Core | BTC/USDT, ETH/USDT | 1h | 12 months | Primary promotion gate |
| Extension | SOL/USDT | 1h | 12 months | Must not degrade core |
| Stress | Top 20 scan universe (frozen list hash) | 1h | 6 months | Frequency / NO_TRADE impact |

Walk-forward folds: use production `config.yaml` → `backtest.walk_forward_*` (train/val/roll/min_folds).  
Acceptance ratio: `oos_pf >= oos_pf_ratio_min * is_pf` per symbol **and** aggregate OOS PF non-inferior to baseline.

### 2.2 Baselines (always compare against)

| ID | Description | Config |
|----|-------------|--------|
| **B0** | Production engine today | `main` config, structure degraded in BT (`book=None`), flow degraded when no history |
| **B1** | B0 + technical simplification branch (if tested) | Document diff in experiment record |
| **B2** | B0 with live-only features **disabled** in research (upper bound on backtest honesty) | Same as B0 for fair comparison |

Every candidate feature **F** runs as **B0+F** vs **B0** under identical bars and fees/slippage.

### 2.3 Metrics (record all)

| Metric | Source | Promotion use |
|--------|--------|----------------|
| OOS profit factor (aggregate + per symbol) | `run_walk_forward` | **Hard gate** |
| OOS vs IS PF ratio | WF acceptance | **Hard gate** |
| Win rate by `score_bucket` | `bucket_stats_from_trades` | Monotonicity check |
| Trade count OOS | WF trades | Min sample (see §2.4) |
| Max drawdown (R) | backtest summary | Soft cap vs baseline |
| NO_TRADE rate change | scan replay optional | Product impact |
| \|live−replay\| score delta | future parity harness | Block if > ε without manifest |

### 2.4 Statistical significance (pragmatic)

We are not a HFT shop with millions of trades. Use **practical** gates:

1. **OOS trades ≥ 80** aggregate across folds (else: **reject** or evidence-only).  
2. **Bucket monotonicity:** for buckets with `n ≥ 30`, higher |score| buckets must not have **>5 pp** lower win rate than adjacent lower bucket (unless documented regime split).  
3. **PF lift:** aggregate OOS PF ≥ **baseline OOS PF** (same run) **or** ≥ **0.05 absolute** with WF pass unchanged.  
4. **No symbol veto:** ETH/BTC each must not show OOS PF **< 0.85 × baseline** for that symbol.

If gates fail → **Reject** or **Evidence / Context / Confidence modifier** path only (see §2.5).

### 2.5 Promotion classes (after experiment)

| Class | Enters synthesizer score? | Where |
|-------|---------------------------|--------|
| **P0 — Reject** | No | — |
| **P1 — Evidence** | No | `structure_events`, `explanation`, replay |
| **P2 — Regime modifier** | No (gates weights/tradeability) | `regime.py` |
| **P3 — Confidence modifier** | No (trust label) | `calibration.py` / `trust_utils.py` |
| **P4 — Lane score (bounded)** | Yes | Single lane owner only |
| **P5 — Synthesizer threshold** | Yes (parameters only) | `config.yaml` via promotion pipeline |

---

## 3. Experiment backlog (ordered)

Priority reflects **parity**, **orthogonality**, and **data availability**—not competitor features.

| Priority | Feature | Default class if weak | Owner lane |
|----------|---------|------------------------|------------|
| R0 | Technical orthogonalization (no new indicator) | P4/P5 | Technical + synthesizer inputs |
| R1 | Long/short ratio | P4 or reject | Flow |
| R2 | Liquidity sweep | P4 or P1 | Structure |
| R3 | Equal highs / equal lows | P4 or P1 | Structure |
| R4 | FVG | P1 or reject | Structure |
| R5 | VWAP | Context / reject | Technical or context |
| R6 | Liquidations | Context / reject | Context |
| R7 | Macro (DXY / yields) regime warning | P2 | Regime |
| R8 | ETF flows | Context | Context |
| R9 | On-chain metrics | Context | Context |

---

## 4. Experiment cards

### R0 — Technical lane orthogonalization (mandatory before new indicators)

**Hypothesis:** Reducing correlated trend/momentum terms improves OOS stability without lowering recall unacceptable.

**Variants:**

| Variant | Change |
|---------|--------|
| T0 | Baseline |
| T1 | Remove EMA200 side when stack score ≠ 0 |
| T2 | T1 + MACD contributes only if sign agrees with stack |
| T3 | T2 + ADX multiplier applies to stack+RSI sub-score only |

**Run:** Core tier, 12m + 18m WF, B0 vs T1/T2/T3.

**Accept:** Best variant beats B0 on aggregate OOS PF **and** WF pass rate ≥ B0; document in promotion record.

**Integrate:** `engine/lanes/technical.py` only; config flags for rollback.

---

### R1 — Long/short ratio (futures)

**Hypothesis:** Positioning crowding adds **orthogonal** information vs funding level alone.

**Data:** Binance global long/short account ratio (or equivalent)—must archive history to bar timestamps for backtest **or** run **live-only shadow** until 90 days archive.

**Variants:**

| Variant | Rule |
|---------|------|
| L0 | Baseline |
| L1 | Z-score of L/S vs 30d, threshold ±2, ±10 flow score |
| L2 | L1 + extreme only (±2.5), ±15 score |
| L3 | Evidence string only (no score) |

**Run:** 6m + 12m; BTC, ETH, SOL; if no history → **defer** scoring, allow L3 shadow.

**Accept (P4):** L1 or L2 passes §2.4 and **flow lane correlation** with funding < 0.5 on sample.

**Reject:** If correlated with funding z > 0.7 and no PF lift.

**Integrate:** `engine/lanes/flow.py`, `DataLayer` fetch; manifest flag `flow_ls_ratio`.

---

### R2 — Liquidity sweep

**Hypothesis:** Stop-run + reclaim patterns improve structure edge in ranging regimes.

**Definitions (test all three):**

| ID | Bullish sweep rule (mirror for bear) |
|----|--------------------------------------|
| S1 | Low < min(low, prior 20 bars) AND close > prior bar low AND close in upper 50% of range |
| S2 | S1 + reclaim above min(low prior 20) |
| S3 | S2 + volume > 20-bar avg |

**Run:** 12m WF; BTC, ETH; report by regime (RANGING vs TRENDING from 4h label at bar).

**Metrics:** OOS PF, precision proxy (TP1 rate on sweep-triggered **hypothetical** entries vs full engine), false positive rate in COMPRESSION.

**Accept (P4):** One definition beats B0 OOS PF **and** does not collapse trade count > 40%; score cap ±15 structure.

**Reject / P1:** If lift only in-sample or only one symbol.

**Integrate:** `engine/lanes/structure.py` + `structure_events.py`; optional SL anchor in `risk.py` **only if** R2 accept + separate micro-experiment on SL.

---

### R3 — Equal highs / equal lows

**Hypothesis:** Liquidity rests at equal swing extremes; improves level quality vs naive clustering.

**Variants:**

| Variant | Rule |
|---------|------|
| E0 | Baseline clustering |
| E1 | Merge swing highs within 0.1% as equal high pool |
| E2 | E1 + require ≥2 touches before level is “active” |

**Run:** 12m WF core tier.

**Accept:** E2 improves OOS PF vs B0 **or** improves bucket monotonicity with same PF.

**Integrate:** `cluster_levels` / structure only.

---

### R4 — Fair value gap (FVG)

**Hypothesis:** 3-candle imbalance zones add incremental edge.

**Variants:**

| Variant | Rule |
|---------|------|
| F0 | Baseline |
| F1 | Classic FVG: bull gap if low[i] > high[i-2], unfilled |
| F2 | F1 + only if gap size > 0.25 ATR |

**Run:** 6m + 12m; BTC, ETH, SOL.

**Default expectation:** **P1 evidence only** unless F2 clears §2.4.

**Accept (P4):** Rare; requires clear PF lift without overfitting (often **reject**).

---

### R5 — VWAP

**Hypothesis:** Session VWAP acts as mean anchor.

**Variants:**

| Variant | Rule |
|---------|------|
| V0 | Baseline |
| V1 | UTC daily VWAP distance in ATR, ±8 technical score |
| V2 | Evidence only: “price above VWAP” in explanation |

**Run:** 12m; **must** fix session anchor (UTC 00:00).

**Default:** **Context / P1**—VWAP rarely passes WF for 1h crypto without session ambiguity.

**Reject for P4:** If performance sensitive to session timezone choice.

---

### R6 — Liquidations

**Hypothesis:** Forced flow predicts short-term continuation/reversal.

**Data:** CoinGlass/Hyblock or exchange—**historical archive required**.

**Phases:**

| Phase | Action |
|-------|--------|
| Phase A | Dashboard only (labeled estimates) — **no experiment** |
| Phase B | Archive 6m liq spikes; join to bars |
| Phase C | Variants: spike z-score → flow evidence vs score |

**Accept:** Unlikely for P4 at 1h; target **P2 warning** (regime) or **P3** (“elevated liquidation day”) if correlated with SHOCK.

**Default:** **Context / dashboard** until Phase B complete.

---

### R7 — Macro (DXY, 10Y yield)

**Hypothesis:** Risk-off days increase false positives for longs.

**Variants:**

| Variant | Rule |
|---------|------|
| M0 | Baseline |
| M1 | If DXY 24h change > +0.8%, reduce long_threshold +5 (synthesizer param) |
| M2 | M1 as **confidence modifier** only (trust string) |

**Run:** 24m daily macro aligned to 1h bars; core crypto.

**Accept:** **P2 or P3** preferred over P4; must not block > 50% of valid trades without PF gain.

**Integrate:** Context fetch → Regime or Trust only.

---

### R8 — ETF flows

**Experiment:** **Deferred** until licensed daily series with immutable snapshots.

**Default:** Context + trust disclaimer (current stub).

---

### R9 — On-chain (MVRV, flows, whales)

**Experiment:** **Deferred**—bar alignment and causality weak at 1h.

**Default:** Context dashboards; **no score**.

---

## 5. Research infrastructure (build order)

These are **enablers**, not product features:

| Step | Deliverable | Unblocks |
|------|-------------|----------|
| 1 | **Experiment log** (`research/experiments/EXP-####.md` template) | Traceability |
| 2 | **Frozen universe file** per run (`research/universes/*.json`) | Survivorship control |
| 3 | **Baseline runner script** (CLI: `python -m research.run --exp R2-S1`) | Repeatability |
| 4 | **FeatureManifest** JSON next to calibration | Live/BT parity |
| 5 | **Promotion record** (`config.promotion.json` with parent hash) | Production gate |
| 6 | **MDS / feature snapshots** (Phase 2 infra) | Same inputs for BT and prod |

*Scripts may be added later; this roadmap defines acceptance before implementation work.*

---

## 6. Experiment record template

```markdown
# EXP-YYYY-NNN: <title>

## Hypothesis
## Variants
## Data & universe hash
## Baseline ID
## Results (table: OOS PF, trades, WF pass, buckets)
## Decision: Reject | P1 | P2 | P3 | P4 | P5
## Integration PR scope (files)
## Rollback plan
```

---

## 7. Cadence

| Activity | Frequency |
|----------|-----------|
| WF calibration (production) | Monthly or post-config change |
| Re-run **B0** benchmark | After any engine merge to `main` |
| New experiment | As prioritized in §3; max **one** P4 candidate per release |
| Parity audit (live vs replay) | Quarterly |

---

## 8. Decision summary table (fill after runs)

| Exp | Status | Decision | Date | Notes |
|-----|--------|----------|------|-------|
| R0 | Implemented (T3 default) | Run WF via `python cli.py research walk-forward --compare` | — | Orthogonalization in engine |
| R1 | Implemented | Run WF when L/S history archived | — | Flow z-score |
| R2 | Implemented | WF compare | — | Structure sweep score |
| R3 | Implemented | WF compare | — | Equal-high clustering |
| R4 | Implemented (events) | WF optional | — | FVG in structure_events |
| R5 | Implemented (evidence) | — | — | UTC session VWAP text |
| R6 | Context stub | Vendor feed | — | `/context/liquidations` |
| R7 | Implemented (regime) | Monitor DXY gate | — | Stooq DXY context |
| R8 | Deferred | Context | — | ETF stub unchanged |
| R9 | Deferred | Context | — | On-chain not in scope |

---

## 9. Final principle

```
Research → Experiment → Walk-forward → Calibration → Production
```

Never:

```
Idea → Implementation → Synthesizer
```

If an experiment is boring and rejects a popular indicator—that is **success**, not failure.

---

*This roadmap does not modify engine behavior until individual experiments complete and pass the promotion gate.*
