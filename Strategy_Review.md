# Downpour Trade AI — Strategy & Competitive Review

**Date:** 2026-08-04  
**Scope:** Read-only review of the deterministic engine vs publicly described [Deeepr.ai](https://deeepr.ai/) capabilities and vs common discretionary playbook concepts (trend filter, liquidity sweep, zones, confirmations, SL/TP).  
**Sources:** Repository code (`engine/`, `api/`, `config.yaml`, `docs/BACKTEST_FIDELITY.md`), Deeepr.ai marketing/pricing page (partial fetch), and third-party blog summaries of Deeepr’s public positioning (not verified product internals).

---

## 1. Current implementation inventory

### Architecture

| Component | Role | Key files |
|-----------|------|-----------|
| **Orchestration** | Fetch data → four analyses → synthesize → plan → calibrate label → structure events | `engine/analyzer.py` |
| **Technical lane** | EMA stack (20/50/200), RSI, MACD hist slope, ADX multiplier, HTF disagreement halving | `engine/lanes/technical.py` |
| **Flow lane** | Funding level/trend/z-score, OI×price regimes, taker buy ratio | `engine/lanes/flow.py` |
| **Structure lane** | Swing S/R clusters, order-book walls (live), volume profile POC/HVN/LVN, breakout/breakdown on volume | `engine/lanes/structure.py` |
| **Regime** | 4h ADX+EMA200 slope → TRENDING_UP/DOWN/RANGING; ATR percentile → SHOCK/COMPRESSION; BTC shock gate for alts | `engine/lanes/regime.py` |
| **Synthesizer** | Regime-weighted lane average; alignment + conflict + adverse-lane + `no_edge` gates; default NO_TRADE | `engine/synthesizer.py` |
| **Risk** | ATR SL with structure buffer; TP1 at nearest opposing S/R or 2R; TP2 at fixed R multiple; min R:R; 1% sizing | `engine/risk.py` |
| **Calibration** | Walk-forward OOS trades → score buckets → HIGH/MODERATE/LOW labels | `engine/calibration.py`, `engine/backtest.py` |
| **Trust (API)** | Bucket stats + walk-forward pass/fail on enriched verdicts | `api/trust_utils.py`, `api/verdict_enrich.py` |
| **Explainability** | Lane evidence → `why` / `why_not` / `risk` | `engine/explanation.py` |
| **Replay** | Ordered timeline from stored JSON (deterministic) | `engine/replay.py` |
| **Structure events** | BOS / CHoCH labels on swings (attached to verdict, not lane score) | `engine/structure_events.py` |
| **Backtest** | Bar walk, no lookahead; degraded structure (no book) and often no taker flow | `engine/backtest.py`, `docs/BACKTEST_FIDELITY.md` |
| **Lifecycle** | Patient vs market entry staging for UI/history | `engine/lifecycle.py` |
| **Context (non-engine score)** | News aggregation, ETF snapshot, liquidity snapshot API, scenario shock on open positions | `api/routes/context.py`, `engine/scenario.py`, `engine/news_aggregator.py` |
| **Coach / Copilot** | Rule-based markdown (no LLM in verdict path; copilot is template over JSON) | `api/coach.py`, `api/copilot.py` |

### Synthesizer philosophy (verified)

- **NO-TRADE by default** unless weighted score, lane alignment, no adverse lane, no structure `no_edge`, no lane conflict, regime tradeable.
- **Regime** reweights lanes (e.g. ranging favors structure; trending favors technical).
- **SHOCK** and large **BTC moves** force non-tradeable for alts.

### Scoring scale

- Lane scores roughly ∈ [-100, 100]; synthesizer thresholds: long ≥ +35, short ≤ -35, ≥2 lanes beyond ±20, conflict if spread > 80 (`config.yaml` → `synthesizer`).

---

## 2. Deeepr.ai — public feature inventory

**Note:** The Google share link (`share.google/NpGEInNAk2ewCUe7X`) did not resolve in automated fetch. Comparison relies on [deeepr.ai](https://deeepr.ai/) homepage snippets, pricing tables, and independent blog descriptions of their **public** positioning. Internal models, prompts, and signal rules are **not** known.

### Publicly marketed capabilities

| Feature | Public description |
|---------|-------------------|
| **Four lanes** | Technical, derivatives/flow, narrative (news/sentiment/ETF), macro (DXY, rates, risk-on/off) |
| **Synthesizer** | Cross-check lanes vs historical accuracy → one verdict with stops/targets |
| **Analyze** | AI trade verdicts (token spend) |
| **Copilot chat** | Natural-language Q&A, scope-locked to Binance-listable crypto |
| **Earth Radar / news** | Geolocated live news globe + feed |
| **Capital / institutional dashboards** | Whales, ETF flows, liquidations, funding, options (tiered) |
| **Scenario simulator** | Stress scenarios (e.g. BTC -5% in an hour) |
| **Telegram alerts** | When user-defined setup fires (paid tiers) |
| **Live strategies + paper trading** | 2–10 strategies by plan |
| **Daily pre-market brief** | Summarized context |
| **Pricing** | Token pool across tools; INR tiers (Trader / Pro / Quant) |

### Classification vs Downpour (objective)

| Deeepr (public) | Downpour | Classification |
|-----------------|----------|----------------|
| Multi-lane market read | Technical + flow + structure + regime | **We already have it** (3 scored lanes + regime; Deeepr adds narrative/macro as lanes) |
| Derivatives / flow | Funding, OI, taker, z-score | **We already have it** (live); Deeepr also cites liquidations/options in dashboards |
| Technical indicators | EMA, RSI, MACD, S/R (blog) | **We already have it** (different EMA periods: 20/50/200 not 9/21) |
| AI synthesizer | Deterministic weighted synthesizer | **Implemented differently** — Deeepr: LLM fusion; Downpour: fixed rules + weights |
| Entry / SL / TP | `build_trade_plan` | **We already have it** (mechanical, explainable) |
| Walk-forward / bucket trust | Walk-forward OOS + trust card | **We do it better** for auditability (same buckets in backtest and labels) |
| Narrative / news lane in **score** | News/context APIs only | **Partially have it** (UI/context); **Missing in engine score** |
| Macro lane in **score** | Macro page + news tags; no DXY lane score | **Partially have it** / **Missing in engine** |
| Copilot NL chat | Deterministic coach + explain copilot | **They do it better** for conversational UX; **We do it better** for traceability |
| Whale / ETF / liquidation dashboards | ETF route, flows snapshot, news | **Partially have it** |
| Scenario simulator | `engine/scenario.py` shock on open positions | **We already have it** (simpler, portfolio-linked) |
| Telegram / live strategies / paper | Alerts rules API; no Telegram executor | **Missing** (by design scope) |
| Token metering / SaaS packaging | Self-hosted API | **Not relevant** to engine philosophy |
| “Historical accuracy” weighting per lane | Regime static weights only | **Partially have it** — no per-lane accuracy learning |

---

## 3. Feature overlap summary

| Overlap area | Downpour | Deeepr (public) |
|--------------|----------|-----------------|
| Lane-based analysis | Yes, deterministic | Yes, AI-combined |
| Flow / derivatives | In engine | In engine + extra dashboards |
| Context / news | Adjacent product surface | Inside “narrative lane” |
| Trust / confidence | Backtest buckets + WF gate | Described as cross-check vs history |
| Alerts | User rules on engine fields | Telegram + setup matching |
| Education | Glossary, engine docs, coach | Copilot + briefs |

---

## 4. Strategy methodology review (code-verified)

### 4.1 Trend filter

| Concept | Status | Where / notes |
|---------|--------|----------------|
| EMA 9 | **Missing** | Not in `engine/indicators.py` usage |
| EMA 21 | **Missing** | — |
| EMA 200 | **Already implemented** | `analyze_technical`: stack 20>50>200; side bias ±`ema200_side` |
| Hard filter: longs only above 200 EMA | **Missing** | No synthesizer gate on EMA200; only score contribution |
| Hard filter: shorts only below 200 EMA | **Missing** | Same |
| Penalize counter-trend | **Partially implemented** | HTF stack disagree → ×0.5; `max_adverse_lane` blocks; regime weights; RSI extremes |
| Strong reversals | **Partially implemented** | RSI oversold/overbought penalties; **CHoCH** in `structure_events` (display, not scored) |

**Recommendation:** Enhance **technical lane** + optionally **synthesizer** with configurable soft penalties (not hard bans) when action opposes 4h `TRENDING_*` from `analyze_regime`, reusing existing regime labels—avoid parallel “trend filter” module. Adding EMA 9/21 alone duplicates EMA 20/50 stack unless backtest proves incremental OOS value.

---

### 4.2 Liquidity sweep

| Concept | Status | Where / notes |
|---------|--------|----------------|
| Liquidity grab / stop hunt | **Missing** as explicit pattern | — |
| Swing failure / wick rejection | **Missing** | No wick/body rules |
| Equal highs/lows sweep | **Missing** | Swings clustered but no equal-level logic |
| Break and reclaim / false break | **Partially implemented** | Breakout/breakdown requires close beyond S/R **and** volume > 20-bar avg; no reclaim-after-sweep |
| Bullish sweep: LL vs prior 20 bars + close back above | **Missing** | Closest: new swing low detection in `detect_swings`, not sweep semantics |

**Enhancement path:** Extend **structure lane** with a deterministic `detect_liquidity_sweep(df, lookback=20)` adding evidence + bounded score (similar to breakout block). Surface in **structure_events** and **replay** for explainability. **Do not** add a second structure system.

**Statistical expectations:**

| Effect | Likely |
|--------|--------|
| Precision | ↑ if sweeps are rare, well-defined |
| Recall | ↓ (fewer raw signals) |
| False positives | Risk ↑ in ranging chop without volume filter |
| Walk-forward | Uncertain until backtested with same degraded-mode caveats |
| Determinism | ↑ if rule is closed-form |

---

### 4.3 Demand / supply zones

| Concept | Status | Where / notes |
|---------|--------|----------------|
| Demand / supply zones | **Implemented differently** | Swing low/high **clusters** → `SRLevel` with `touches`; proximity in ATR |
| Order blocks / SMC origin candles | **Missing** | No last opposing candle before impulse |
| Impulsive move detection | **Partially** | Breakout/breakdown + ADX trend multiplier in technical |
| Volume “origin” | **Partially** | Volume profile POC/HVN/LVN |

**Recommendation:** Treat clustered supports with `touches ≥ 3` as **existing zone logic**. Enhancement: tag strongest cluster as “validated zone” in evidence (wording only) or small score bump on retest—**not** full SMC vocabulary unless backtest-validated.

---

### 4.4 Second touch logic

| Concept | Status | Where / notes |
|---------|--------|----------------|
| Touch counting | **Already implemented** | `cluster_levels` → `touches`; breakout requires `min_touch_breakout: 3` |
| First vs second test | **Missing** | No bar-index memory of tests |
| Wait for second touch | **Missing** | `patient` entry snaps to nearest S/R but does not require retest |

**Recommendation:** Optional **`patient` + config flag** `require_retest` in **risk/synthesizer**: only allow LONG if price closed back above support after touch (second interaction). Default **off** to preserve scan frequency. Fits philosophy if implemented as gate with explicit `reasons[]` string.

---

### 4.5 Confirmation candle

| Pattern | Status |
|---------|--------|
| Bullish/bearish engulfing, hammer, shooting star, pin bar, body/wick ratio, momentum candle | **Missing** (no matches in repo) |

**Recommendation:** If added, use **soft scoring in technical lane only** (+/- bounded points) with evidence strings—**not** hard synthesizer rules (avoids brittle pattern overfitting). Candle features must use **completed bar** only (same as backtest bar loop). Alternative: **evidence-only** in structure_events without score until walk-forward justifies weights.

---

### 4.6 Stop loss logic

**Current (`engine/risk.py`):**

- Base: `entry ± atr_sl_multiplier × ATR` (1.5× default).
- If structure level is tighter: SL beyond `nearest_support/resistance` with `support_sl_buffer_atr`.
- Invalid risk or R:R < `min_reward_risk` → downgrade to NO_TRADE.

| Method | In engine? |
|--------|------------|
| Demand zone / support | Yes (nearest support) |
| Liquidity sweep low | No |
| ATR | Yes (fallback) |
| Swing low | Implicit via swing-cluster support price |

**Statistical note:** Combining structure + ATR is already a **max(structure, ATR)**-style rule (whichever gives valid stop). Adding sweep low would **enhance structure lane output** feeding the same risk function—not a new SL engine.

**Recommendation:** After sweep detection, pass `sweep_low` in structure `values`; risk prefers `min(support, sweep_low)` for longs with buffer. Compare in backtest vs current baseline using existing `run_backtest`.

---

### 4.7 Take profit logic

**Current:**

- TP1: nearest resistance (long) / support (short), else 2× risk.
- TP2: `tp2_rr_multiplier` × risk (2.0 default).
- Gate: min R:R 1.2 to TP1.

| Target type | Status |
|-------------|--------|
| Previous high/low | Via nearest swing resistance/support |
| Supply/demand | Same S/R levels |
| Liquidity | Not explicit (walls not used in TP) |
| ATR multiples | Only via risk distance |
| Dynamic | No trailing; timeout exit in backtest (`trade_timeout_bars: 48`) |

**Recommendation:** Optional TP1 at **POC or next HVN** from existing volume profile in structure `values`—single enhancement point, evidence logged. Avoid duplicate TP calculators.

---

## 5. Statistical impact matrix (proposed enhancements)

| Enhancement | Precision | Recall | False positives | Trade frequency | Overfit risk | Walk-forward | Confidence | Explainability | Determinism |
|-------------|-----------|--------|-----------------|-----------------|--------------|--------------|------------|----------------|-------------|
| Regime-aligned soft trend gate | ↑ | ↓ | ↓ counter-trend | ↓ | Low if few params | Likely ↑ | ↑ bucket purity | ↑ | ↑ |
| Liquidity sweep (structure) | ↑? | ↓ | ↑ in chop | ↓ | Medium | Test required | ↑ if OOS improves | ↑ | ↑ |
| Second-touch gate (optional) | ↑ | ↓↓ | ↓ | ↓↓ | Low | ↑ | ↑ | ↑ | ↑ |
| Candle patterns (soft score) | ? | ↑ | ↑ | ↑ | **High** | Often ↓ | ↓ unless WF passes | ↑ | ↑ |
| Sweep-aware SL | ↑ SL quality | — | ↓ bad R:R trades | ↓ | Medium | Test | ↑ | ↑ | ↑ |
| POC/HVN TP1 | Neutral | — | — | — | Low | Test | Neutral | ↑ | ↑ |
| EMA 9/21 parallel to 20/50 | Duplicate | — | — | — | **High** | Unlikely | ↓ interpretability | ↓ | ↑ |

---

## 6. Integration map (no duplicate systems)

| Idea | Integrate into |
|------|----------------|
| Trend / EMA playbook | **Technical** + **Regime** weights; optional **Synthesizer** gate |
| Liquidity sweep | **Structure** score + **structure_events** + **Replay** |
| Zone retest / second touch | **Structure** touch state or **Synthesizer** + **Lifecycle** |
| Candle confirmation | **Technical** soft score only |
| SL beyond sweep | **Structure** `values` → **Risk** |
| TP at HVN/POC | **Structure** `values` → **Risk** |
| Narrative/macro scoring | **New weighted inputs** only if deterministic rules—else keep **Context** UI separate (avoids LLM in core) |
| Deeepr-style NL copilot | **API** layer only; never replace **Synthesizer** |

---

## 7. Where Downpour is stronger

1. **Deterministic verdict path** — Every score traceable to `evidence[]` and `config.yaml`.
2. **Walk-forward calibration** — OOS trades feed buckets; dashboard WF pass/fail; documented fidelity limits.
3. **NO-TRADE default** — Lane conflict, adverse lane, `no_edge`, R:R, SHOCK regime.
4. **Live microstructure** — Order-book walls in structure (with spoof caps).
5. **Trust card** — Same `score_bucket` in backtest, calibration, and API.
6. **Replay timeline** — Ordered deterministic narrative from JSON.
7. **No LLM in the trading decision** — Copilot/coach explain without changing engine output.

---

## 8. Where Downpour is weaker (vs Deeepr public surface)

1. **Narrative and macro not in engine score** — Context feeds exist but do not move verdict.
2. **Conversational UX** — Deeepr Copilot; Downpour rule-based coach.
3. **Alert delivery** — No Telegram/native “setup fired” product integration.
4. **Institutional dashboard breadth** — Whales, options, liquidations depth (public Deeepr tiers).
5. **Playbook patterns** — Sweeps, candle confirmations, second-touch discipline not encoded.
6. **Backtest/live parity** — Structure/flow weaker in calibration (documented)—can depress WF pass rate vs live feel.
7. **EMA set** — Discretionary traders often expect 9/21/200; engine uses 20/50/200.

---

## 9. Recommended enhancements (priority)

1. **Structure: liquidity sweep detector** (bounded score + events + optional SL input) — backtest A/B first.
2. **Optional second-touch / retest gate** tied to `patient` mode — config default off.
3. **Regime-aware counter-trend penalty** in synthesizer (soft, evidence in `reasons`).
4. **Trust UX** — Surface per-symbol WF detail on dashboard (frontend only; data exists in `/calibrate`).
5. **TP1 refinement** using existing POC/HVN when nearer than swing level and R:R still ≥ min.
6. **Calibration hygiene** — Re-run after structure changes; align marketing copy with `BACKTEST_FIDELITY.md`.

---

## 10. Recommended NOT to implement

| Item | Why |
|------|-----|
| Parallel “strategy builder” scoring engine | Duplicates lanes + synthesizer |
| LLM inside synthesizer | Breaks determinism, calibration, trust |
| Full SMC package (order blocks, BOS/CHoCH as hard gates) | CHoCH/BOS already labeled; SMC gates overlap S/R + breakout logic |
| EMA 9 + 21 alongside 20 + 50 | Redundant trend features; overfitting risk |
| Hard mandatory 200 EMA filter | Conflicts with ranging-regime structure edge; use soft/regime conditional |
| Duplicate candle-pattern library as hard rules | High overfit; weak walk-forward unless OOS-proven |
| Copy Deeepr token/chat product | Different product philosophy; keep copilot explain-only |
| Narrative sentiment LLM score without reproducible inputs | Not backtestable |

---

## 11. Existing concepts that already solve the same problem

| Discretionary idea | Downpour equivalent |
|--------------------|---------------------|
| “Trade with trend” | EMA stack + 4h regime + HTF halving + ADX multiplier |
| “Key level” | Swing S/R clusters + walls + volume profile |
| “Crowded positioning” | Funding + OI + taker flow |
| “Don’t trade chaos” | SHOCK regime, BTC move gate, lane conflict → NO_TRADE |
| “Need confirmation” | Min aligned lanes + min score + min R:R (not candle-specific) |
| “Institutional context” | News/ETF/flows routes (informational) |
| “Why this signal?” | explanation + replay + trust + attribution |

---

## 12. Engineering complexity (rough)

| Enhancement | Complexity | Test burden |
|-------------|------------|-------------|
| Sweep detection | Medium | High (backtest + WF) |
| Second-touch gate | Medium | Medium |
| Regime trend penalty | Low | Medium |
| Candle soft scores | Medium | High |
| POC TP1 | Low | Medium |
| Dashboard WF detail | Low (UI) | Low |

---

## 13. Final verdict

**Downpour Trade AI is already a lane-based, deterministic alternative to Deeepr’s publicly described AI-trading-intelligence stack.** Core overlap: technical + flow + synthesis + plan + context dashboards. Architectural divergence: Downpour optimizes **provability** (evidence, walk-forward, buckets, NO-TRADE); Deeepr optimizes **breadth and conversational delivery** (narrative/macro lanes, Copilot, Telegram, paper strategies, tokenized SaaS).

The discretionary playbook in the review (9/21/200 filter, liquidity sweep, demand zones, second touch, confirmation candles) is **partially present** as swing S/R, volume breakouts, touch counts, and EMA 20/50/200—but **not** as a classical price-action rule set. The highest-value, philosophy-aligned gaps are **liquidity sweep + optional retest gating** inside the **structure** and **synthesizer** paths, validated through existing **backtest/walk-forward**, not new parallel systems.

**Do not** chase feature parity with Deeepr’s AI/chat/alert product layer unless product strategy shifts; **do** strengthen structure and calibration honesty so live scans, trust labels, and WF gates tell one consistent story.

---

*This document is analytical only. It does not change engine behavior. Re-verify against `main` after material engine commits.*
