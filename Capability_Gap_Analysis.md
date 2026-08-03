# Downpour Trade AI — Capability Gap Analysis & Expansion Strategy

**Date:** 2026-08-04  
**Type:** Read-only engineering review (no code changes).  
**Method:** Full inspection of `engine/`, `api/`, `config.yaml`, `docs/BACKTEST_FIDELITY.md`, and context modules. External products compared from **public** positioning only.

**Legend:** ✅ Fully Implemented · 🟡 Partially Implemented · 🟠 Implemented Differently · 🔴 Missing · ⚪ Not Applicable · ❌ Should Not Be Added

---

## 1. Executive Summary

Downpour Trade AI is a **deterministic, lane-based crypto signal engine** (technical + flow + structure, gated by regime) with **mechanical risk**, **walk-forward calibration**, **trust/replay/explanation**, and **context APIs** (news, macro snapshot, flows dashboard) that **explicitly do not feed the synthesizer**.

**Strengths:** Provable evidence chains, NO-TRADE default, live order-book structure (with spoof caps), Binance spot + USDM futures via CCXT, backtest/WF pipeline, scan rejection analytics.

**Gaps vs broad “market intelligence” checklists:** ICT-style sweeps/FVG/order blocks, candle/chart patterns, on-chain metrics, liquidation/options data, tradfi macro series (DXY, yields, CPI calendar), long/short ratio, and **any LLM narrative scoring**.

**Strategic direction:** Extend **Structure**, **Flow**, **Regime**, **Trust**, and **Explainability**—not parallel indicator stacks or duplicate lanes. Context stays **dashboard-first** until a metric is **historically backtestable** at bar time with stable APIs.

Related prior work: `Strategy_Review.md` (playbook + Deeepr high-level).

---

## 2. Current Capability Matrix (Engine vs Context)

| Layer | In synthesizer score? | Primary location |
|-------|------------------------|------------------|
| Technical (EMA/RSI/MACD/ADX) | Yes | `engine/lanes/technical.py` |
| Flow (funding/OI/taker/z) | Yes | `engine/lanes/flow.py` |
| Structure (S/R, book, VP) | Yes | `engine/lanes/structure.py` |
| Regime (4h trend, SHOCK, BTC gate) | Gates + weights | `engine/lanes/regime.py` |
| BOS/CHoCH labels | No (verdict metadata) | `engine/structure_events.py` |
| News / RSS | No | `engine/news_aggregator.py` |
| Macro (CoinGecko global) | No | `engine/data.py` → `get_macro_snapshot()` |
| ETF flows | No (stub) | `api/context_fetch.py` |
| Flows dashboard | No | `api/routes/flows.py` |
| Correlation / scenario | No | `engine/correlation.py`, `engine/scenario.py` |
| Calibration / trust | Labels + API | `engine/calibration.py`, `api/trust_utils.py` |

---

## 3. Module 1 — Technical Analysis (Feature Audit)

| Capability | Status | Location / notes | Scoring vs evidence |
|------------|--------|------------------|---------------------|
| Market Structure (HH/HL/LH/LL) | 🟡 | Implicit via `detect_swings` + CHoCH HH/LL logic in `structure_events.py`; **not** scored | **Evidence** first; optional small structure score if formalized |
| BOS | 🟡 | `structure_events.py` (bull/bear break of last swing) | **Evidence** (+ replay); optional bounded structure boost after WF test |
| CHoCH | 🟡 | `structure_events.py` | **Evidence** only today |
| MSS (Market Structure Shift) | 🔴 | Not named; closest = CHoCH | If added, alias CHoCH—do not duplicate |
| Trendlines | 🔴 | — | Low priority; subjective unless regression-based |
| Support & Resistance | ✅ | `structure.py`: swing clusters, touches, ATR distance | **Scoring** (support/resistance/breakout) |
| Supply & Demand | 🟠 | Same as S/R clusters (not SMC “zones”) | **Scoring** via proximity/touches |
| Order Blocks | 🔴 | — | ❌ Avoid SMC clone unless defined as last opposite candle + impulse (then structure extension) |
| Breaker / Mitigation Blocks | 🔴 | — | ❌ Too ICT-specific without OOS proof |
| Fair Value Gaps (FVG) | 🔴 | — | Could be deterministic gap rule in **structure**; **evidence-first** |
| Liquidity Pools | 🟡 | Swing highs/lows + book walls ≈ resting liquidity; no “pool” label | **Scoring** (walls capped) |
| Equal Highs / Lows | 🔴 | Clustering merges nearby swings, no equality test | **Structure** enhancement candidate |
| Premium & Discount | 🔴 | — | Could map to range position vs POC (VP exists) |
| Fibonacci | 🔴 | — | ⚪ Optional dashboard; weak determinism for auto levels |
| EMA 9 | 🔴 | — | ❌ Duplicates 20/50 stack |
| EMA 20 | ✅ | `technical.py` | **Scoring** |
| EMA 50 | ✅ | `technical.py` | **Scoring** |
| EMA 100 | 🔴 | — | ❌ Redundant with 50/200 |
| EMA 200 | ✅ | `technical.py`, `regime.py` (4h slope) | **Scoring** + regime |
| VWAP | 🔴 | — | Session VWAP possible in **technical**; needs session anchor policy |
| ATR | ✅ | `indicators.py`, structure/risk/regime | **Scoring** (distance) + **risk** |
| RSI | ✅ | `technical.py` | **Scoring** |
| MACD | ✅ | `technical.py` (histogram slope) | **Scoring** |
| Bollinger Bands | 🔴 | — | Optional **technical** soft score; not required |
| Supertrend | 🔴 | — | Overlaps ADX/EMA trend |
| Volume | 🟡 | Breakout/breakdown volume vs 20-bar avg in `structure.py` | **Scoring** |
| Delta Volume | 🔴 | — | Needs agg trades / footprint feed |
| Footprint | 🔴 | — | ❌ Not on Binance public API for retail |
| Volume Profile | ✅ | `_volume_profile` in `structure.py` (POC/HVN/LVN) | **Scoring** (POC/HVN) |
| Candlestick Patterns | 🔴 | — | If added: **soft technical score** only after WF |
| Chart Patterns | 🔴 | — | Too subjective for core engine |

---

## 4. Module 2 — Smart Money Concepts (ICT)

| ICT Concept | Status | Equivalent in Downpour? | Deterministic? | Recommendation |
|-------------|--------|-------------------------|----------------|--------------|
| Internal / External liquidity | 🟡 | Swing levels + book walls | Partial | Extend **structure** labeling, not new lane |
| BSL / SSL | 🟡 | Swing highs/lows as liquidity magnets | Yes | Tag in **structure_events** |
| Liquidity Sweep | 🔴 | — | Yes (rule-based) | **Structure** — high priority |
| Stop Hunt | 🔴 | — | Yes if sweep defined | Same as sweep |
| Judas Swing | 🔴 | — | Subjective | ❌ Defer |
| Power of Three (PO3) | 🔴 | — | Subjective | ❌ Not for core |
| OTE (Fib 62–79%) | 🔴 | — | Medium | ❌ Unless tied to existing S/R |
| Dealing Range | 🟡 | POC + range between nearest S/R | Partial | **Evidence** from structure values |
| Session Liquidity | 🔴 | — | Needs session defs (UTC) | **Regime** or structure session flags |
| Kill Zones | 🔴 | — | Discretionary time windows | ❌ Dashboard optional only |
| SMT Divergence | 🔴 | — | Needs correlated symbol series | **Flow/structure** research item |

**Principle:** Do not adopt ICT vocabulary without a **closed-form rule**. Prefer enhancing swing + sweep + reclaim in **Structure Lane** over importing full SMC.

---

## 5. Module 3 — Futures Data

| Metric | Status | Implementation | Provider today | Priority |
|--------|--------|----------------|----------------|----------|
| Open Interest | ✅ | `DataLayer.get_oi`, flow lane | Binance USDM (CCXT) | — |
| Funding Rate | ✅ | `get_funding`, flow lane | Binance USDM | — |
| Long/Short Ratio | 🔴 | Not fetched | Binance has global L/S endpoints (not wired) | **P1** — cheap, fits **flow** |
| Liquidations | 🔴 | Word in news sentiment only | CoinGlass/Hyblock (paid) | **P2** dashboard; **P3** score if historical |
| Short / Long Squeeze | 🟡 | Inferred via OI+price+funding combos | Derived | Extend **flow** evidence strings |
| Basis | 🔴 | — | Futures vs spot index | **P2** flow context |
| Premium (futures vs spot) | 🔴 | — | CCXT mark/index | **P2** |
| Options OI | 🔴 | — | Deribit etc. | **P3** dashboard |
| Max Pain | 🔴 | — | Options vendor | ⚪ Dashboard only |
| Gamma Exposure (GEX) | 🔴 | — | Vendor-specific | ⚪ Not core philosophy |

**Missing providers:** Liquidations heatmap (CoinGlass ~$100+/mo tier), options (Deribit API), institutional L/S (exchange or Coinglass).

**Reliability:** Binance via CCXT is production-proven in codebase; third-party adds SLA and cost.

**Integration owner:** **Flow Lane** for anything that affects positioning; never a second “derivatives lane.”

---

## 6. Module 4 — On-Chain Analysis

| Metric | Status | Signal vs context |
|--------|--------|-------------------|
| Exchange Inflow/Outflow | 🔴 | Context unless bar-aligned history |
| Exchange Reserve | 🔴 | Context |
| Whale Wallets | 🔴 | Context (deferred in `context_fetch.py`) |
| Miner Reserve / Selling | 🔴 | Context |
| Dormant Coins | 🔴 | Context |
| Realized Price / MVRV / SOPR / NUPL | 🔴 | Context; slow-moving |
| Active / New Addresses | 🔴 | Context |
| Hash Rate / Difficulty | 🔴 | Context (BTC macro) |
| Stablecoin Supply / Ratio | 🔴 | Context; macro liquidity |

**Do we need them?** For **short-horizon 1h signals**, most on-chain metrics are **informational** (low update relevance vs noise). They improve **narrative dashboards**, not proven edge in current backtest framework.

**Best providers (public knowledge):** Glassnode, CryptoQuant, Nansen — all **paid**, rate-limited.

**Recommendation:** ⚪ **Dashboard + macro page** first; **do not** add On-Chain Lane until historical series can be joined **deterministically** to backtest bars. ❌ **Should not** add LLM “on-chain narrative” to synthesizer.

---

## 7. Module 5 — Institutional Activity

| Capability | Status | Location |
|------------|--------|----------|
| ETF Inflows/Outflows | 🔴 live data | Stub: `fetch_etf_context()` |
| Corporate Buy/Sell | 🔴 | News keywords only (`news_aggregator`) |
| Government/Treasury Holdings | 🔴 | — |
| Whale Transactions | 🔴 | Deferred per audit docs |
| OTC Deals | 🔴 | — |

**Implementation path:** Licensed ETF feed (Bloomberg/Farside/CF Benchmarks) → **context API** → optional **regime warning** (e.g. extreme flow day) **without** changing lane math until backtested.

**Dashboard vs score:** **Dashboard only** until SLA + historical file; then consider **confidence modifier** in **trust layer**, not raw score bump.

---

## 8. Module 6 — Macroeconomics (Calendar & Series)

| Series | Status | In engine? |
|--------|--------|------------|
| CPI / Core CPI / PPI | 🟡 | RSS from BLS feeds → **news/macro category**, not parsed numbers |
| NFP / Unemployment | 🟡 | Same (headlines only) |
| FOMC / Fed | 🟡 | Fed RSS in `FEED_SOURCES` |
| GDP / Retail / PMI / Consumer Confidence | 🟡 | Headline-only via macro RSS |
| Interest Rates / Treasury Yields | 🔴 | No yield curve data |
| Inflation / M2 | 🔴 | — |

**Should they block trades?** Today: **only via regime** (SHOCK ATR percentile, BTC move)—not calendar.

**Recommended policy:**

| Action | When |
|--------|------|
| **Block trades** | Only deterministic gates already in **regime** (extend with scheduled “event window” if ever added—config-driven UTC windows, not NLP) |
| **Reduce confidence** | Trust layer disclaimer when macro headline category=`macro` and keyword match in last N hours—**optional, evidence-only** |
| **Warnings only** | **Default** for news/macro |
| **Separate Macro Lane** | ❌ **Not yet** — would duplicate context; if added, must be **rule-based** (e.g. DXY 24h change), not LLM |

---

## 9. Module 7 — Global Markets

| Asset | Status | Location |
|-------|--------|----------|
| DXY | 🔴 | — |
| Gold / Silver | 🔴 | — |
| Nasdaq / S&P / Dow | 🔴 | — |
| Oil | 🔴 | — |
| VIX | 🔴 | — |
| Bonds | 🔴 | — |
| BTC dominance / total mcap | ✅ | `get_macro_snapshot()` — **context** |

**Correlation value:** Useful for **alt regime** (already BTC 1h gate) and scenario shock (`correlation_vs_btc`).

**Placement:** **Regime** extension (risk-off flag from DXY + BTC correlation) or **context module**—not a seventh scored lane without WF proof.

---

## 10. Module 8 — News Intelligence

**Current:** `engine/news_aggregator.py` — multi-source RSS + Bybit/OKX APIs; dedupe; symbol tags; **3-level sentiment** (Bullish/Bearish/Neutral) via keyword lists; categories **`news` | `macro` | `exchange`**.

| Requested tag | Status |
|---------------|--------|
| ETF, SEC, Trump, Fed, CPI, FOMC, Binance, Coinbase, Hack, War, Regulation, Adoption, Company buy/sell, Mining, Stablecoin | 🟡 | Partially via **keywords** in `BULLISH_WORDS`/`BEARISH_WORDS` and **feed source** (not a structured taxonomy) |
| Impact Low/Med/High/Extreme | 🔴 | — |

**File header:** *“context only, never fed to synthesizer.”*

**Should news affect scores?** **No** for current philosophy—non-reproducible in backtest, high narrative risk.

**Should news pause signals?** Optional **future**: config **event blackout windows** tied to **exchange** category maintenance RSS—deterministic, testable.

**Preserve determinism:** Any future news influence must use **frozen keyword lists + timestamps**, logged in **replay**, never LLM classification in the hot path.

---

## 11. Module 9 — Market Psychology

| Source | Status | Notes |
|--------|--------|-------|
| Fear & Greed | 🔴 | Free APIs exist (Alternative.me) — **macro dashboard** |
| Social / X / Reddit / YouTube | 🔴 | Noisy, bot-inflated |
| Google Trends | 🔴 | — |
| Retail FOMO / Panic | 🟡 | Proxy: funding z-score, taker ratio, RSI extremes |

**Verdict:** **Unreliable** for core scoring; **deterministic proxies already in flow/technical**. ❌ Do not add sentiment ML. ⚪ Fear & Greed as **context tile** only.

---

## 12. Module 10 — Decision Engine Coverage

| Factor | Synthesizer / lanes | Notes |
|--------|---------------------|-------|
| Trend | ✅ | Technical + regime weights |
| Market Structure | 🟡 | S/R scored; BOS/CHoCH evidence only |
| Liquidity | 🟡 | Book walls + swings; no sweep |
| Order Block | 🔴 | — |
| FVG | 🔴 | — |
| Volume | 🟡 | Breakout volume, VP |
| Delta | 🔴 | — |
| Funding | ✅ | Flow |
| Open Interest | ✅ | Flow |
| ETF Flow | 🔴 | Context stub |
| Whale Activity | 🔴 | — |
| Stablecoin Flow | 🔴 | — |
| DXY / Gold / Nasdaq | 🔴 | — |
| CPI / FOMC | 🔴 in score | RSS context only |
| News | 🔴 in score | Context |
| Risk | ✅ | `build_trade_plan` + NO_TRADE downgrade |
| Entry Confirmation | 🟡 | Lane alignment + min R:R; no candle confirm |

**Better integration:** Missing items map to **Structure** (liquidity, FVG), **Flow** (L/S ratio, basis), **Regime** (macro shock flags)—not new synthesizers.

---

## 13. AI Output Review (Verdict & UI vs Checklist)

| Output field | Present? | Where |
|--------------|----------|-------|
| Market Bias | 🟠 | `action` + `weighted_score` (not “bias” label) |
| Confidence Score | 🟠 | `confidence` string from calibration buckets, not 0–100 |
| Trend Strength | 🟡 | ADX in technical values; regime name |
| Liquidity Direction | 🟡 | Structure evidence (walls, S/R) |
| Institutional Activity | 🔴 | Not in verdict |
| Whale Activity | 🔴 | — |
| ETF Flow | 🔴 | — |
| News Impact | 🔴 | — |
| Macro Impact | 🔴 | — |
| Technical Score | ✅ | Lane score |
| Fundamental Score | 🔴 | No fundamental lane |
| Risk Level | 🟡 | R:R, size, SL/TP in `trade_plan` + explanation |
| Suggested Action | ✅ | `action` + plan |

**Add without changing engine:** Enrich **API/UI projection layer** (`verdict_enrich`, trust card, pair hero) with derived fields:

- `bias`: LONG/SHORT/NEUTRAL from action/score band  
- `trend_strength`: ADX bucket from lane values  
- `confidence_tier`: parse HIGH/MODERATE/LOW from confidence string  
- `context_summary`: pull news count + macro dominance (read-only)

All **computed from existing JSON**—deterministic, no new logic in synthesizer.

---

## 14. Overlap With Existing Engine (Do Not Duplicate)

| If you want… | Already have… | Enhance instead of… |
|--------------|---------------|---------------------|
| Demand zones | Swing support clusters | New “zone lane” |
| Liquidity | Swings + walls | Separate liquidity engine |
| Trend filter | EMA 20/50/200 + regime | EMA 9/21 stack |
| Market structure | BOS/CHoCH events | Parallel MS indicator |
| Confidence | WF buckets + trust | LLM confidence |
| News impact | RSS + sentiment tags | Narrative lane in score |
| Institutional | Flow funding/OI | Whale lane |
| Scenarios | `simulate_shock` | Full portfolio Monte Carlo in engine |

---

## 15. Missing Capabilities — Standard Assessment Template

For each **high-priority missing** item below: why missing, should exist, owner lane, complexity, stats, risks, impacts.

### 15.1 Liquidity sweep (ICT-style)

| Dimension | Assessment |
|-----------|------------|
| Why missing | Structure focused on proximity/breakout, not wick-through-reclaim |
| Should exist? | **Yes**, as bounded structure feature |
| Owner | **Structure** + **structure_events** + optional **risk** SL |
| Complexity | Medium |
| Statistical value | May ↑ precision, ↓ frequency |
| Overfitting risk | Medium in chop |
| Determinism | ↑ if rule is closed-form |
| Explainability | ↑ |
| Calibration | Requires backtest with `book=None` unchanged |
| Performance | Low CPU |

### 15.2 Long/Short ratio (futures)

| Dimension | Assessment |
|-----------|------------|
| Why missing | Not wired in `DataLayer` |
| Should exist? | **Yes** for flow crowding |
| Owner | **Flow** |
| Complexity | Low |
| Statistical value | Moderate |
| Overfitting | Low with z-score style |
| Determinism | ↑ |
| Calibration | Backtest must store historical L/S or skip in degraded mode |
| Performance | One extra API call per symbol |

### 15.3 Liquidations (dashboard)

| Dimension | Assessment |
|-----------|------------|
| Why missing | Cost + no vendor in repo |
| Should exist? | **Context/dashboard** first |
| Owner | **API context**, not synthesizer |
| Complexity | Medium integration |
| Statistical value | Uncertain for 1h |
| Overfitting | High if scored naively |
| Determinism | ⚠ unless historical archive |
| Recommendation | CoinGlass-style **labeled estimate** |

### 15.4 On-chain / whale / ETF live

| Dimension | Assessment |
|-----------|------------|
| Why missing | SLA, cost, philosophy (context-only) |
| Should exist? | **Dashboard** yes; **score** later |
| Owner | Context → maybe **trust disclaimer** |
| Complexity | High (contracts, $) |
| Calibration | Poor until bar-aligned history |

---

## 16. Capabilities We Should NOT Implement

| Capability | Reason |
|------------|--------|
| LLM synthesizer or narrative score | Breaks determinism, backtest, trust |
| Full ICT / SMC package as hard gates | Overlaps S/R; subjective labels |
| Footprint / delta without exchange feed | Not available on current stack |
| Duplicate EMA sets (9/21/100) | Indicator sprawl |
| Parallel “Fundamental Lane” | No reproducible inputs |
| Social sentiment scoring | Noise, manipulation |
| Strategy builder / paper trading engine | Product scope (see Competitive Enhancement Plan deferrals) |
| TradingView-style 500 indicators | Conflicts with “stronger intelligence, not more indicators” |
| Auto-executing Telegram trades | Execution risk, regulatory |

---

## 17. Capabilities To Enhance (Priority)

| Priority | Enhancement | Lane / layer |
|----------|-------------|--------------|
| P0 | Document + UI projection fields (bias, trend_strength, tiers) | Trust / API enrich |
| P1 | Liquidity sweep + equal highs/lows | Structure |
| P1 | Binance long/short ratio | Flow |
| P2 | Scheduled macro **blackout** config (exchange maint RSS) | Regime |
| P2 | Basis / mark premium | Flow |
| P2 | Fear & Greed + DXY (free/yahoo) | Context + regime flag |
| P3 | Liquidation dashboard (vendor) | Context |
| P3 | ETF flow feed when licensed | Context → trust note |
| P3 | Session tags (UTC) for structure | Structure / regime |

---

## 18. Data Provider Recommendations

| Need | Provider options | Est. cost | Use |
|------|------------------|-----------|-----|
| Spot/futures OHLCV, funding, OI | Binance (CCXT) | Free tier + rate limits | ✅ In use |
| Global crypto macro | CoinGecko | Free / rate limit | ✅ In use |
| News | Owned RSS + exchange APIs | Free | ✅ In use |
| Liquidations / heatmap | CoinGlass, Hyblock | ~$50–300+/mo | Dashboard |
| On-chain | Glassnode, CryptoQuant | $$$ | Context |
| Whale labels | Arkham, Nansen | $$$ | Context |
| ETF flows | Farside, Bloomberg | $$$ | Context |
| Tradfi (DXY, VIX) | Yahoo Finance, FRED | Free/low | Regime context |
| Options | Deribit | API free tier limited | Dashboard |

---

## 19. Cost & Complexity Estimates

| Initiative | Eng weeks (1 dev) | Ongoing $/mo | Risk |
|------------|-------------------|--------------|------|
| Structure sweep + events | 1–2 | $0 | Medium WF |
| L/S ratio in flow | 0.5 | $0 | Low |
| UI/trust projection fields | 0.5–1 | $0 | Low |
| DXY + Fear&Greed context | 1 | $0 | Low |
| CoinGlass liq dashboard | 1–2 | $100+ | Medium |
| ETF live feed | 2+ | $200+ | Vendor lock-in |
| On-chain lane (historical) | 4+ | $300+ | High scope creep |

---

## 20. Statistical Impact Analysis (Summary)

| Change type | Precision | Recall | False positives | Trade freq | WF | Calibration |
|-------------|-----------|--------|-----------------|------------|-----|-------------|
| Structure sweep | ↑ likely | ↓ | ↑ in range if unfiltered | ↓ | Must re-test | Bucket shift |
| Flow L/S ratio | ↑ modest | ↔ | ↓ crowding trades | ↔ | Test | Improves flow fidelity |
| News → score | ? | ↑ | ↑↑ | ↑ | ↓ likely | **Harm** |
| Macro lane rules | ↑ selective | ↓ | ↓ on event days | ↓ | Test | Trust alignment |
| More indicators | ↔ | ↔ | ↑ | ↔ | ↓ overfit | **Harm** |

---

## 21. Competitive Comparison (Public Capability View)

| Capability | Downpour | Deeepr.ai | TradingView | CoinGlass | Glassnode | CryptoQuant | Nansen |
|------------|----------|-----------|-------------|-----------|-----------|-------------|--------|
| Deterministic signals | **Ahead** | Behind (AI) | N/A (charting) | Partial | N/A | Partial | N/A |
| Multi-lane fusion | Comparable | **Ahead** (4 lanes + AI) | User-built | Data only | N/A | N/A | N/A |
| Walk-forward trust | **Ahead** | Unknown public | N/A | N/A | N/A | N/A | N/A |
| Charting / indicators | Behind | Behind | **Ahead** | Partial | N/A | N/A | N/A |
| Liquidations dashboard | Behind | Public tier | Add-ons | **Ahead** | Some | Some | N/A |
| On-chain metrics | Behind | Marketing | N/A | Limited | **Ahead** | **Ahead** | **Ahead** |
| News / narrative | Comparable context | **Ahead** (lane) | N/A | News | N/A | N/A | Labels |
| Order book walls | **Ahead** (in engine) | Unknown | DOM | Partial | N/A | N/A | N/A |
| Funding/OI | Comparable | **Ahead** depth | Scripts | **Ahead** | Some | **Ahead** | N/A |
| Paper/strategies | N/A | **Ahead** | Paper | N/A | N/A | N/A | N/A |
| Explainability/replay | **Ahead** | Copilot NL | Manual | N/A | N/A | N/A | N/A |

**Not relevant to philosophy:** TV indicator marketplace, Nansen wallet labels as auto-trade signals, Deeepr token metering, community features.

---

## 22. Recommended Implementation Roadmap

### Phase A — Truth layer (0–2 weeks)
- Expose derived **output projections** from existing verdict JSON (UI/API only).
- Dashboard WF per-symbol detail from `/calibrate` (already available).

### Phase B — Structure edge (2–4 weeks)
- Liquidity sweep + equal highs/lows; replay + evidence.
- Backtest A/B; re-run walk-forward.

### Phase C — Flow completeness (1–2 weeks)
- Long/short ratio + optional basis/premium in **flow** with evidence.
- Extend `/flows/snapshot` parity with engine inputs.

### Phase D — Context depth (parallel, optional $)
- Fear & Greed + DXY on macro page.
- Liquidation **link-out or vendor tile** (labeled estimates).
- ETF feed when budget allows.

### Phase E — Regime policy (2 weeks)
- Optional **event blackout** from exchange RSS timestamps (deterministic).
- Never block via NLP news alone.

### Explicitly out of roadmap
- On-chain scoring lane, LLM narrative, ICT full stack, footprint, social sentiment, duplicate indicators.

---

## 23. Final Principle Checklist

Every approved enhancement must:

- [ ] Use **existing lanes** or **context** boundaries  
- [ ] Log **evidence strings** reproducible in **replay**  
- [ ] Be **skippable in backtest** with documented degradation  
- [ ] Avoid **second synthesizers** or **shadow scores**  
- [ ] Improve or honestly document **trust/calibration** impact  

**Verdict:** Downpour should not pursue “indicator parity” with TradingView or “data parity” with Glassnode. It should pursue **the best deterministic fusion of price, positioning, and structure** with **provable calibration**—using external data as **context** until history and WF justify scoring.

---

*End of document. No repository code was modified.*
