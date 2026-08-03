# Downpour Trade AI — Competitive Enhancement Plan

**Version:** 2.0  
**Date:** 2026-08-04 (rev. product review)  
**Scope:** Additive enhancements only — no replacement of the deterministic signal engine, architecture, or existing features.

**v2.0 changes:** Added **Trust Layer**, **Replay Mode**, **Engine Health**, **Calibration Dashboard**, **Signal Lifecycle**, **Scanner Heatmap**, **Scan Explainability**, **Compare Signals**, **AI Coach** (education-only), **Explain the Engine** per lane; reordered roadmap into four product phases; explicit **will not build** list (Earth Globe, Community, Strategy Builder, Paper Trading, unreliable Whale Dashboard).

**Primary competitor researched:** [Deeepr.ai](https://deeepr.ai/) (landing page, pricing, public feature descriptions, YouTube demos).  
**Secondary benchmarks:** TradingView, CoinGlass, CryptoQuant, Glassnode, Nansen, Hyblock, DefiLlama, Messari, Santiment, Lookonchain, Arkham.

**Public references (illustrative, not copied):**

| Source | What they do well | Our additive response |
|--------|-------------------|------------------------|
| [Deeepr.ai](https://deeepr.ai/) | Four-lane synthesis, Telegram, Copilot Q&A, globe + news, capital-flow dashboards, scenario simulator | Keep our deterministic lanes; add **context dashboards** + **explain-only Copilot** over verdict JSON |
| [CoinGlass](https://www.coinglass.com/) | Funding compare, liquidation heatmaps, OI aggregates | **Funding dashboard** + optional liq heatmap overlay (labeled as modeled) |
| [TradingView](https://www.tradingview.com/) | Screener, watchlists, alert builder | **Watchlists** + **alert rules** wired to our scan results |
| [Nansen / Glassnode](https://nansen.ai/) | Wallet labels, macro cycle metrics | **Read-only context panels** — never feed unlabeled AI into verdict |

---

## 1. Executive summary

**Deeepr.ai** positions as *AI crypto trading intelligence*: multi-lane analysis (Technical, Flow, **Narrative**, **Macro**), synthesizer with tiered confidence, Copilot chat, geolocated news “Earth Radar,” institutional dashboards (ETF, whales, liquidations, funding, options), scenario stress-testing, strategy builder, paper/live strategies, and Telegram delivery — token-based pricing (₹999–₹2,499/mo).

**Downpour Trade AI** differentiates on **determinism, auditability, and honest NO-TRADE defaults**. Our engine already covers technical, flow, structure (S/R + book walls + volume profile), regime gating, risk math, walk-forward calibration, explainability, API, dashboard, history, backtests, glossary, and Telegram.

**Strategic stance:** Do **not** become a black-box AI signal product. **Do** surround the engine with trust, context, discovery, and workflow — while every trade recommendation still flows from the existing synthesizer + calibration.

**Primary competitive wedge (v2):** Deeepr *markets* confidence tiers. Downpour **proves** confidence — historical win rate, profit factor, walk-forward pass/fail, trade count, and freshness — on every signal page. See §4.13 Trust Card.

---

## 2. Phase 1 — Deeepr.ai feature inventory

Grouped per requested taxonomy.

### Intelligence

| Feature | Description (public) |
|---------|---------------------|
| Multi-lane analyze | Technical, Flow, Narrative, Macro — independent biases |
| Lane tier labels | HIGH / MOD / LOW per lane |
| Synthesizer | Cross-check lanes vs historical accuracy → single verdict |
| Verdict output | LONG/SHORT/WAIT-style with entry, SL, TP1, TP2, R:R |
| Copilot | Natural-language Q&A scoped to Binance-listable crypto, live prices |
| Daily pre-market brief | Narrative summary of market |
| Scenario simulator | Stress basket vs macro shock (e.g. BTC −5% / 1h) |
| Strategy builder | User-defined rules / automation (Quant tier) |
| Paper + live strategies | 2–10 live strategies by tier |

### Market data

| Feature | Description |
|---------|-------------|
| Live prices | Anchored in Copilot and analyze |
| Derivatives | Funding, OI, order-flow dashboards |
| Institutional flows | ETF flows, whale wallet moves |
| Liquidations | Dashboard + scenario impact |
| Options | Listed under Pro derivatives dashboards |

### AI

| Feature | Description |
|---------|-------------|
| LLM Copilot | Answers “what’s BTC doing”, “should I add here” |
| AI analyze | Marketing positions verdicts as AI-driven (multi-source) |
| Token metering | Monthly token pool across tools |

### Portfolio

| Feature | Description |
|---------|-------------|
| Basket / positions | Scenario sim references user LONG positions and stops |
| Hedge modeling | e.g. PAXG absorption in shock example |

### User experience

| Feature | Description |
|---------|-------------|
| Earth globe + news | Geolocated headlines |
| Drawer UX | Whales / ETF / liq / scenarios under globe |
| Pricing tiers | Free trial tokens → Trader → Pro → Quant |
| Mobile-friendly marketing | Heavy visual, scroll narrative |

### Alerts

| Feature | Description |
|---------|-------------|
| Telegram signals | On setup fire |
| Tier-gated | Pro+ |

### Visualization

| Feature | Description |
|---------|-------------|
| Lane cards | Four columns with bias + tier |
| Verdict card | Entry/SL/TP layout |
| Globe | News + institutional drawer |

### Dashboard

| Feature | Description |
|---------|-------------|
| Capital Flows | Trader tier |
| Institutional & Derivatives | Pro tier |
| Compare plans table | Feature matrix on site |

### Analytics

| Feature | Description |
|---------|-------------|
| Historical lane accuracy | Implied for synthesizer tiers |
| R:R display | On verdict |

### Risk

| Feature | Description |
|---------|-------------|
| Scenario cascade | Funding shift, OI −%, stop triggers |
| “WAIT” guidance | Copilot discourages poor R:R chase |

### Education

| Feature | Description |
|---------|-------------|
| Marketing explainers | Pipeline story on landing |
| Implicit via Copilot | Q&A teaching |

### Community

| Feature | Description |
|---------|-------------|
| Community support | Trader tier |

### Trading

| Feature | Description |
|---------|-------------|
| Paper trading | Pro |
| Live strategies | Pro/Quant |

### News

| Feature | Description |
|---------|-------------|
| Geolocated feed | Earth Radar |
| Narrative lane | News/sentiment in analyze |

### Macro

| Feature | Description |
|---------|-------------|
| Macro lane | DXY, gold, risk-on framing |
| Macro shock presets | Scenario simulator |

### Narrative

| Feature | Description |
|---------|-------------|
| Narrative lane | ETF inflows, Fed tone, etc. |
| Tier LOW/MIXED | Shown on marketing examples |

### Research

| Feature | Description |
|---------|-------------|
| Copilot research | Ad-hoc questions |
| Briefs | Daily pre-market |

### Performance

| Feature | Description |
|---------|-------------|
| Lane historical tiers | Marketing claim |
| Strategy performance | Quant tier (implied) |

### Settings

| Feature | Description |
|---------|-------------|
| Account / billing | Token plans |
| Cancel anytime | Stated on site |

---

## 3. Phase 2 — Feature comparison matrix (Downpour vs Deeepr + notes)

Legend: **AE** Already Exists · **BT** Better than Ours · **WT** Worse than Ours · **NA** Not Applicable · **CI** Can Improve · **MI** Missing

| Category | Feature | Classification | Notes |
|----------|---------|----------------|-------|
| Intelligence | Deterministic multi-lane engine | **AE** / **BT** | We are auditable; Deeepr is LLM-heavy |
| Intelligence | Technical lane | **AE** | EMA, RSI, MACD, ADX, HTF |
| Intelligence | Flow lane | **AE** | Funding, OI, taker; z-score added |
| Intelligence | Structure / S&R / walls | **AE** | Book walls + VP; Deeepr markets similar “depth” story |
| Intelligence | Regime gate | **AE** | SHOCK/COMPRESSION/TREND/RANGING |
| Intelligence | Narrative lane | **MI** | Deeepr lane; we should add **context-only** narrative panel, not verdict lane |
| Intelligence | Macro lane | **CI** | Spec regime macro partial; add **macro context dashboard** |
| Intelligence | Synthesizer strict NO-TRADE | **AE** / **BT** | Our default honesty is stronger |
| Intelligence | Walk-forward calibration | **AE** / **BT** | Deeepr marketing implies history; we document OOS |
| Intelligence | Per-lane tier (HIGH/MOD/LOW) | **CI** | Map from calibration buckets per lane |
| Intelligence | Copilot / NL Q&A | **MI** | Add **explain-only** Copilot over our JSON |
| Intelligence | “WAIT” / no-trade coaching | **CI** | Extend `explanation.why_not` in UI |
| Intelligence | Scenario simulator | **MI** | Add **portfolio shock preview** using existing risk math |
| Intelligence | Strategy builder / automation | **NA** / **MI** | Optional long-term; not core to Downpour |
| Intelligence | Paper / live trading | **NA** | Execution out of scope |
| Market data | Binance OHLCV, funding, OI, book | **AE** | ccxt public |
| Market data | Multi-exchange aggregates | **MI** | CoinGlass-style; optional API |
| Market data | Liquidation heatmap (modeled) | **MI** | Overlay or link-out + API |
| Market data | ETF flows | **MI** | Context dashboard |
| Market data | Whale wallet feed | **MI** | Labeled transfers (third-party API) |
| Market data | Options data | **MI** | Pro-only competitor feature |
| Market data | On-chain labeled wallets | **MI** | Nansen-class; context only |
| AI | LLM-generated signals | **WT** | We reject by design |
| AI | LLM summarize verdict | **CI** | Allowed if **cannot change** action/score |
| AI | NL query → fetch our API | **MI** | Copilot reads `/analyze`, `/scan` |
| Portfolio | Portfolio heat / max positions | **CI** | Spec in risk; wire UI + enforcement |
| Portfolio | Correlation-adjusted exposure | **CI** | Spec partial |
| Portfolio | User basket in scenario sim | **MI** | Uses open verdicts from DB |
| UX | Dashboard scan table | **AE** | |
| UX | Pair detail + lanes | **AE** | |
| UX | Glossary | **AE** / **BT** | Deeepr has marketing copy only |
| UX | TradingView embed | **AE** | |
| UX | Earth globe + geo news | **MI** | Optional **News context** strip |
| UX | Dark theme | **AE** | |
| UX | Mobile polish | **CI** | Tables, touch targets |
| UX | Keyboard shortcuts | **MI** | Nice-to-have |
| Alerts | Telegram on LONG/SHORT | **AE** | |
| Alerts | Alert builder (user rules) | **MI** | |
| Alerts | Email / Discord / Slack / webhooks | **MI** | |
| Viz | Score gauge | **AE** | |
| Viz | Liquidity / book heatmap on chart | **CI** | We compute walls; add **historical book snapshot** replay |
| Viz | Liquidation heatmap on chart | **MI** | Modeled layer |
| Dashboard | Funding dashboard (multi-symbol) | **MI** | |
| Dashboard | Capital flows summary | **MI** | Aggregated scan + flow lane stats |
| Analytics | History + outcomes | **AE** | |
| Analytics | Backtest / calibration tables | **AE** | |
| Analytics | Signal confidence **history** chart | **MI** | |
| Analytics | Signal attribution (which lane drove score) | **CI** | Decompose weighted score in UI |
| Analytics | Trade journal | **MI** | User notes + link to verdict id |
| Analytics | Performance analytics (user PnL) | **NA** | We don’t execute trades |
| Risk | ATR sizing, SL/TP, R:R gate | **AE** | |
| Risk | Vol-adjusted sizing | **CI** | Config exists; surface in UI |
| Risk | Daily/weekly loss limits | **CI** | Spec in risk module |
| Education | In-app glossary | **AE** | |
| Education | Morning/evening recap | **MI** | Generated from **scan JSON**, not LLM signals |
| Community | Shared watchlists | **MI** | Long-term |
| News | Geolocated feed | **MI** | RSS/API with **no effect** on verdict |
| Macro | BTC dominance / stable dominance | **CI** | Spec; implement read-only + regime hooks |
| Research | Saved research notes | **MI** | Notebook per symbol |
| Performance | Live win-rate from outcomes | **CI** | History page basic; expand |
| Settings | User prefs (TF default, watchlist) | **MI** | |
| Infra | FastAPI REST | **AE** | |
| Infra | PostgreSQL | **CI** | Production uses SQLite; optional Postgres |
| Infra | Redis cache | **CI** | In-process TTL today; Redis for multi-instance |
| Infra | Hetzner + Vercel | **AE** | |

### Assumed-inventory features (per product owner — treat as AE for roadmap, CI for UX depth)

These are treated as **Already Exists** in engine/spec; enhancement focus is **visualization, labeling, and API exposure** without replacing logic:

- Multi-timeframe confirmation · Volume Profile · Market Structure · **BOS / CHoCH** · Swing detection · Long/Short ratio · Correlation · BTC/stable dominance · Portfolio risk · Explainability

---

## 4. Phase 3 — Enhancement specs (Missing / Can Improve)

Detailed specs for **priority** items. Others summarized in §10 roadmap.

---

### 4.1 Signal confidence history visualization

| Field | Detail |
|-------|--------|
| **Purpose** | Show how confidence labels and outcomes evolved for a symbol/bucket over time |
| **Business value** | Trust + credibility vs Deeepr “tier” marketing; proves calibration honesty |
| **Difficulty** | Medium |
| **Est. time** | 1–2 weeks |
| **Dependencies** | `verdicts` + `outcomes` tables populated; calibration buckets |
| **UI** | `/history` or `/pair/[symbol]` chart: confidence label + resolved outcome |
| **Backend** | Aggregate query on history; optional `confidence_snapshots` table |
| **Database** | Optional column `bucket` on verdicts; index by symbol/time |
| **API** | `GET /confidence-history?symbol=&limit=` |
| **Performance** | Low; indexed reads |
| **Infrastructure** | None |
| **Optional vs core** | **Core** (trust) |

---

### 4.2 Explain-only Copilot (NL over verdict JSON)

| Field | Detail |
|-------|--------|
| **Purpose** | Answer “why LONG?” in plain language **without** changing scores or verdicts |
| **Business value** | Parity with Deeepr Copilot while preserving determinism |
| **Difficulty** | Medium–High |
| **Est. time** | 2–3 weeks |
| **Dependencies** | LLM API key; strict prompt: only cite `lanes[].evidence`, `reasons`, `trade_plan` |
| **UI** | Chat drawer on pair page; disclaimer banner |
| **Backend** | `POST /copilot/explain` — input: symbol/tf or verdict_id; output: markdown |
| **Database** | Optional chat log (user opt-in) |
| **API** | New route; rate limit |
| **Performance** | External LLM latency; cache by verdict hash |
| **Infrastructure** | LLM provider billing |
| **Optional vs core** | **Optional** (Pro tier candidate) |

**Rule:** Copilot **must not** emit entry/SL/TP unless identical to `trade_plan` in JSON.

---

### 4.3 Funding & derivatives dashboard

| Field | Detail |
|-------|--------|
| **Purpose** | CoinGlass-style multi-symbol funding, OI change, taker skew for scanned pairs |
| **Business value** | Flow lane context at a glance |
| **Difficulty** | Medium |
| **Est. time** | 1–2 weeks |
| **Dependencies** | Existing `DataLayer`; scan pair list |
| **UI** | `/dashboard/flows` or section on Dashboard |
| **Backend** | `GET /flows/snapshot?symbols=` batch fetch |
| **Database** | Cache snapshots optional |
| **API** | New read-only endpoint |
| **Performance** | Batch ccxt; respect rate limits |
| **Infrastructure** | None |
| **Optional vs core** | **Core** |

---

### 4.4 Liquidity map replay (structure enhancement)

| Field | Detail |
|-------|--------|
| **Purpose** | Show **historical** bid/ask wall zones on chart (Arxion/CoinGlass concept) — complements existing wall detection |
| **Business value** | Deeepr “whale wall” story with **our** deterministic book math |
| **Difficulty** | High |
| **Est. time** | 3–4 weeks |
| **Dependencies** | Store periodic book snapshots or replay from cached polls |
| **UI** | Overlay on pair page chart (canvas layer or lightweight-charts) |
| **Backend** | Snapshot job every N seconds during scan; `book_snapshots` table |
| **Database** | Time-series snapshots (retention policy) |
| **API** | `GET /structure/liquidity-map?symbol=&from=&to=` |
| **Performance** | Storage-heavy; downsample |
| **Infrastructure** | Disk on Hetzner |
| **Optional vs core** | **Optional** |

---

### 4.5 Watchlists + custom scanner filters

| Field | Detail |
|-------|--------|
| **Purpose** | User-defined symbol lists; run scan subset; TradingView-style workflow |
| **Business value** | Retention; reduces noise vs top-20 only |
| **Difficulty** | Medium |
| **Est. time** | 2 weeks |
| **Dependencies** | Auth (optional anonymous localStorage first) |
| **UI** | Watchlist sidebar; “Scan my list” |
| **Backend** | `POST /scan?symbols=BTC/USDT,ETH/USDT` or watchlist id |
| **Database** | `watchlists` table if authenticated |
| **API** | Extend `/scan`, `/pairs` |
| **Performance** | Same as scan |
| **Infrastructure** | None |
| **Optional vs core** | **Core** |

---

### 4.6 Alert builder + webhooks

| Field | Detail |
|-------|--------|
| **Purpose** | User rules: e.g. “Telegram if LONG and confidence MODERATE+ and score &gt; 40” |
| **Business value** | Deeepr Pro alerts without black box |
| **Difficulty** | Medium |
| **Est. time** | 2 weeks |
| **Dependencies** | Telegram; optional webhook URL |
| **UI** | `/settings/alerts` |
| **Backend** | Evaluate rules post-scan; dedupe 4h (existing) |
| **Database** | `alert_rules` |
| **API** | CRUD `/alerts/rules` |
| **Performance** | Negligible |
| **Infrastructure** | None |
| **Optional vs core** | **Optional** |

---

### 4.7 Morning / evening market recap

| Field | Detail |
|-------|--------|
| **Purpose** | Deterministic brief from last scan: regime counts, actionable list, BTC/ETH summary |
| **Business value** | Deeepr “daily brief” without narrative LLM hallucination |
| **Difficulty** | Low–Medium |
| **Est. time** | 1 week |
| **Dependencies** | Scan results in DB |
| **UI** | `/brief` or email/Telegram digest |
| **Backend** | Template renderer over JSON; optional LLM **summary only** with fixed facts |
| **Database** | Store brief text per day |
| **API** | `GET /brief?period=morning` |
| **Performance** | Low |
| **Infrastructure** | Cron / APScheduler |
| **Optional vs core** | **Optional** |

---

### 4.8 Scenario simulator (portfolio shock)

| Field | Detail |
|-------|--------|
| **Purpose** | “BTC −5% in 1h” → show impact on **open paper positions** from stored verdicts |
| **Business value** | Deeepr Pro simulator; uses our risk fields |
| **Difficulty** | Medium |
| **Est. time** | 2–3 weeks |
| **Dependencies** | User portfolio definition (manual entry or tracked verdicts) |
| **UI** | `/risk/scenarios` |
| **Backend** | Shock beta from correlation lane; recompute SL hit probability (heuristic) |
| **Database** | `portfolio_positions` optional |
| **API** | `POST /scenarios/run` |
| **Performance** | CPU light |
| **Infrastructure** | None |
| **Optional vs core** | **Optional** |

---

### 4.9 Narrative & news context panel (non-verdict)

| Field | Detail |
|-------|--------|
| **Purpose** | Headlines + tags (bullish/bearish/neutral) **beside** verdict, never in synthesizer |
| **Business value** | Deeepr Narrative lane UX without polluting deterministic score |
| **Difficulty** | Medium |
| **Est. time** | 2 weeks |
| **Dependencies** | News RSS or CryptoPanic API |
| **UI** | Collapsible “Market context” on pair page |
| **Backend** | `GET /context/news?symbol=` |
| **Database** | Cache headlines 15 min |
| **API** | Read-only |
| **Performance** | External API |
| **Infrastructure** | API key |
| **Optional vs core** | **Optional** |

---

### 4.10 Macro context dashboard

| Field | Detail |
|-------|--------|
| **Purpose** | BTC dominance trend, total mcap vs EMA50, stablecoin share — **regime inputs visible** |
| **Business value** | Transparency for alt signals; spec §8 CoinGecko context |
| **Difficulty** | Medium |
| **Est. time** | 1–2 weeks |
| **Dependencies** | CoinGecko `/global` cached |
| **UI** | `/macro` or regime badge drill-down |
| **Backend** | Extend `analyze_regime` evidence + snapshot endpoint |
| **Database** | `macro_snapshots` hourly |
| **API** | `GET /macro/snapshot` |
| **Performance** | Low |
| **Infrastructure** | None |
| **Optional vs core** | **Core** (for alt traders) |

---

### 4.11 BOS / CHoCH chart labels

| Field | Detail |
|-------|--------|
| **Purpose** | Visual labels for break of structure / change of character on pair chart |
| **Business value** | Competitor “structure” literacy |
| **Difficulty** | Medium |
| **Est. time** | 1–2 weeks (if logic exists); +2 if net-new detection |
| **Dependencies** | Structure lane swing logic |
| **UI** | Annotations list + optional TV plugin later |
| **Backend** | Expose `structure.values` + detected events in `/analyze` |
| **Database** | None |
| **API** | Extend verdict JSON |
| **Performance** | Low |
| **Infrastructure** | None |
| **Optional vs core** | **Core** (UX) |

---

### 4.12 PostgreSQL + Redis (scale path)

| Field | Detail |
|-------|--------|
| **Purpose** | Multi-instance API, durable cache, no SQLite lock |
| **Business value** | Growth without engine rewrite |
| **Difficulty** | Medium |
| **Est. time** | 1 week |
| **Dependencies** | Docker compose services |
| **UI** | None |
| **Backend** | SQLAlchemy URL; Redis for cache + scan lock |
| **Database** | Migration from SQLite |
| **API** | Unchanged |
| **Performance** | Improved concurrency |
| **Infrastructure** | Hetzner managed or containers |
| **Optional vs core** | **Optional** until &gt;1 API replica |

---

### 4.13 Trust Card (per signal page) ⭐ Core differentiator

Every pair/verdict view shows a **Provable Confidence** panel (data from calibration + live outcomes, never LLM):

| Field | Source |
|-------|--------|
| Confidence | Current label + numeric bucket score if applicable |
| Historical win rate | OOS calibration for score bucket |
| Backtested trades | `n` from calibration |
| Profit factor | Bucket PF |
| Average R | Bucket avg_r |
| Max drawdown (R) | Bucket max_drawdown_r |
| Walk-forward | Passed / Failed + date |
| Last updated | `data_as_of_utc` + calibration `last_calibrated_utc` |

| Field | Detail |
|-------|--------|
| **Purpose** | Prove confidence vs competitor marketing |
| **Business value** | Trust = moat |
| **Difficulty** | Medium |
| **Est. time** | 1–2 weeks |
| **Dependencies** | `GET /calibrate`, `GET /backtest-stats`, outcome resolver |
| **UI** | `TrustCard` on `/pair/[symbol]` + expandable on Dashboard rows |
| **Backend** | `GET /trust?symbol=&tf=` aggregates calibration bucket + recent outcome WR |
| **Database** | Read existing calibration + outcomes |
| **API** | New read-only endpoint |
| **Performance** | Low |
| **Optional vs core** | **Core — Phase 1** |

---

### 4.14 Confidence history (time series + outcomes) ⭐

Visual: confidence % (or bucket) over time with WIN/LOSS/OPEN per emitted LONG/SHORT.

| Field | Detail |
|-------|--------|
| **Purpose** | Show whether confidence labels predict outcomes |
| **Business value** | “Almost nobody shows this” — retention + credibility |
| **Difficulty** | Medium |
| **Est. time** | 1–2 weeks |
| **UI** | Chart on History + pair page tab |
| **Backend** | Join `verdicts` + `outcomes` + stored confidence string |
| **API** | `GET /confidence-history?symbol=&limit=` |
| **Optional vs core** | **Core — Phase 1** |

---

### 4.15 Signal attribution (weighted lane bars) ⭐

Decompose weighted score into lane contributions (technical / flow / structure / regime weight effects).

| Field | Detail |
|-------|--------|
| **Purpose** | Instant “why LONG” without reading every evidence line |
| **UI** | Horizontal bar chart per lane on pair page + VerdictCard |
| **Backend** | Return `attribution: { lane: contribution }` from synthesizer (additive field, no logic change) |
| **Est. time** | ~1 week |
| **Optional vs core** | **Core — Phase 1** |

---

### 4.16 Replay mode (signal timeline) ⭐

Click any historical or live signal → stepped timeline of **deterministic events** that led to verdict (not VAR video — structured event log):

Example steps: EMA stack aligned → funding flipped → OI rise → BOS detected → synthesizer LONG.

| Field | Detail |
|-------|--------|
| **Purpose** | Education + audit trail |
| **Business value** | High differentiation |
| **Difficulty** | High |
| **Est. time** | 3–4 weeks |
| **Dependencies** | Persist `VerdictEvent[]` at analyze time OR reconstruct from evidence timestamps |
| **UI** | `/pair/[symbol]/replay?id=` or modal on History |
| **Backend** | Store event list in verdict payload or side table |
| **Database** | `verdict_events` JSON column |
| **Optional vs core** | **Core — Phase 2** |

---

### 4.17 Engine health dashboard ⭐

Operational transparency for pro users:

| Check | Meaning |
|-------|---------|
| API | `/health` ok |
| Binance OHLCV | Last fetch age |
| Funding | Last success |
| Order book | Last success |
| Macro (CoinGecko) | Last success / skipped |
| Calibration | Freshness + running job |
| Cache | Verdict/book cache stats |
| DB | Writable |

| Field | Detail |
|-------|--------|
| **UI** | `/status` or footer “Engine health” drill-down |
| **Backend** | Extend `/health` with dependency probes |
| **Est. time** | 1 week |
| **Optional vs core** | **Core — Phase 2** (can ship minimal in Phase 1) |

---

### 4.18 Calibration dashboard (beyond tables)

| Field | Example |
|-------|---------|
| Last calibration | Yesterday 04:12 UTC |
| Pairs calibrated | BTC, ETH, SOL, … |
| Total trades (OOS) | 12,408 |
| Current PF | 2.08 |
| Current WR | 63% |
| OOS passed | YES / NO |
| Walk-forward folds | 4 |

| Field | Detail |
|-------|--------|
| **UI** | Upgrade `/backtests` with summary header + run job status |
| **Backend** | Expose `walk_forward` from calibration JSON |
| **Est. time** | 1 week |
| **Optional vs core** | **Core — Phase 2** |

---

### 4.19 Signal lifecycle

State machine per tracked verdict:

`Detected → Waiting → Confirmed → Entry hit → TP1 → TP2 → Closed (SL/TP/Timeout)`

| Field | Detail |
|-------|--------|
| **Purpose** | Visual pipeline vs static “LONG” chip |
| **Dependencies** | Outcome tracker (exists); optional “entry hit” from price poll |
| **UI** | Stepper on History + pair page for open signals |
| **Est. time** | 2 weeks |
| **Optional vs core** | **Core — Phase 2** |

---

### 4.20 Scanner heatmap

Grid: symbols × color by verdict (LONG/SHORT/NO_TRADE/WAIT-style neutral); group/filter by regime, confidence bucket, sector tag (manual map).

| Field | Detail |
|-------|--------|
| **UI** | `/dashboard/heatmap` or toggle on Dashboard |
| **Est. time** | 1–2 weeks |
| **Optional vs core** | **Core — Phase 2** |

---

### 4.21 Scan explainability (“why 243 rejected”)

Aggregate NO-TRADE reasons from last scan: weak trend, low score, poor R:R, regime block, structure no_edge, lane conflict.

| Field | Detail |
|-------|--------|
| **Purpose** | Prove selectivity — NO-TRADE as product feature |
| **Backend** | Store scan summary histogram; optional light pass recording top `reasons[]` |
| **UI** | “Scan report” drawer after scan completes |
| **Est. time** | 2 weeks |
| **Optional vs core** | **Core — Phase 2** |

---

### 4.22 Compare signals (side-by-side)

BTC vs ETH: lane scores, regime, confidence, trust metrics in two columns.

| Field | Detail |
|-------|--------|
| **UI** | `/compare?a=BTC/USDT&b=ETH/USDT` |
| **Backend** | Parallel `/analyze` (cached) |
| **Est. time** | 1 week |
| **Optional vs core** | **Phase 2–3** |

---

### 4.23 Explain the Engine (lane encyclopedia)

Per lane permanent docs in-app (extends Glossary):

- What it measures · Indicators · Strengths · Weaknesses · When ignored · How weighted in each regime

| Field | Detail |
|-------|--------|
| **UI** | `/engine` or links from each `LanePanel` header |
| **Content** | Static MD/JSON aligned with `config.yaml` |
| **Est. time** | 3–5 days content + page |
| **Optional vs core** | **Core — Phase 1–2** |

---

### 4.24 AI Coach (education-only, not Copilot)

**Copilot:** “Why LONG?” → cites engine JSON.  
**Coach:** “I keep entering before confirmation” → behavioral/educational patterns, **never** new entries/SL/TP, **never** trading advice.

| Field | Detail |
|-------|--------|
| **UI** | Separate tab; strict disclaimer |
| **Backend** | LLM with guardrails; no market orders |
| **Est. time** | 2–3 weeks |
| **Optional vs core** | **Phase 4** |

---

## 4B. Explicitly deferred — will NOT build (now)

| Item | Rationale |
|------|-----------|
| **Earth Globe / geolocated news UI** | Does not increase trading edge; skip visual clone of Deeepr |
| **Community / social** | Not now — support burden |
| **Strategy builder / auto execution** | Too early; conflicts with deterministic product focus |
| **Paper trading** | Low priority vs trust + explainability |
| **Whale dashboard** | Only if **reliable labeled data** contract; otherwise marketing noise |
| **LLM-generated signals** | Permanent ban — augment only |

**Deprioritized from v1 plan:** Morning brief (optional later), collaborative watchlists, public API marketplace.

---

## 5. Principles (additive only)

| Instead of (reject) | Do (accept) |
|---------------------|-------------|
| Replace confidence engine with LLM tiers | Trust Card + confidence history + OOS calibration |
| Replace structure with AI walls | Liquidity replay + wall evidence on chart |
| Replace regime with “AI risk score” | Macro dashboard + SHOCK gate visibility |
| Merge narrative into synthesizer score | Side panel “context only” |
| Auto-trading strategies | Alert builder + Telegram/webhooks |
| Copy Deeepr token pricing | Keep free tier dashboard; monetize Copilot/coach later |
| Earth globe for news | Skip; optional text news in Phase 3 only if needed |
| Whale dashboard without data SLA | Defer |

### AI roles (strict separation)

| Tool | Allowed | Forbidden |
|------|---------|-----------|
| **Explain-only Copilot** | Paraphrase `lanes`, `reasons`, `trade_plan`, Trust Card | New signals, new prices, override verdict |
| **AI Coach** | Education, process, reading the engine docs | Trading advice, entries, sizing |
| **Deterministic engine** | All LONG/SHORT/NO_TRADE | — |

### What v1 plan got right (product sign-off)

- Preserved deterministic engine, explainability, calibration, NO TRADE philosophy — workflow/context only.
- Explain-only Copilot, confidence history, funding dashboard, signal attribution, watchlists, alert builder — all aligned with product direction.

---

## 6. Phase 5–6 — Cross-platform idea bank

| Idea | Source inspiration | Downpour additive use |
|------|-------------------|------------------------|
| Liquidation heatmap | CoinGlass, Hyblock | Modeled overlay; label “estimate” |
| Fear & Greed index | CMC, Alternative.me | Macro panel only |
| Correlation explorer | TradingView, Bloomberg-style | Heatmap of scan pairs vs BTC |
| Sector / narrative rotation | Nansen, Messari | Tag pairs; no score impact |
| Exchange flow charts | CryptoQuant, Glassnode | BTC/ETH context widget |
| Whale alerts | Lookonchain, Arkham | Push to Telegram **separate channel** from signals |
| ETF flow tracker | Deeepr, Bloomberg | Dashboard tile |
| Economic calendar | Forex platforms | Overlay “high impact” hours; regime caution flag |
| Screener filters | TradingView | Filter scan results: regime, score, verdict |
| Replay mode | Arxion liquidity map | Replay verdict + price for education |
| Email digests | Generic SaaS | Morning brief |
| Discord/Slack | Bot integrations | Webhook on actionable scan |
| Advanced charting | TradingView | Keep embed; add our overlays gradually |
| Institution dashboard | Messari Pro | Aggregate scan health, API usage, calibration freshness |

---

## 7. Prioritized roadmap (v2 — product phases)

### Phase 1 — Trust, context, discovery (ship first)

| # | Item | Spec |
|---|------|------|
| 1 | Confidence history + outcomes | §4.14 |
| 2 | Signal attribution (lane bars) | §4.15 |
| 3 | Trust Card on pair page | §4.13 |
| 4 | Funding dashboard | §4.3 |
| 5 | Macro dashboard | §4.10 |
| 6 | BOS / CHoCH visualization | §4.11 |
| 7 | Watchlists (+ scan subset) | §4.5 |
| 8 | Explain the Engine (lane docs) | §4.23 |

**Goal:** Prove confidence, show *why* signals exist, reduce scan noise — without LLM in the verdict path.

---

### Phase 2 — Audit trail & workflow

| # | Item | Spec |
|---|------|------|
| 1 | Replay mode (event timeline) | §4.16 |
| 2 | Signal lifecycle stepper | §4.19 |
| 3 | Alert builder | §4.6 |
| 4 | Explain-only Copilot | §4.2 |
| 5 | Scanner heatmap | §4.20 |
| 6 | Calibration dashboard (summary UX) | §4.18 |
| 7 | Scan explainability (rejection histogram) | §4.21 |
| 8 | Engine health dashboard | §4.17 |

---

### Phase 3 — Context depth (non-verdict)

| # | Item | Spec |
|---|------|------|
| 1 | Scenario simulator | §4.8 |
| 2 | Liquidity map replay | §4.4 |
| 3 | News context panel | §4.9 |
| 4 | ETF context | §6 idea bank |
| 5 | Whale context | §4B — only with reliable feed |
| 6 | Correlation explorer | §6 |
| 7 | Compare signals | §4.22 |

---

### Phase 4 — Education & pro workflow

| # | Item | Spec |
|---|------|------|
| 1 | AI Coach (education-only) | §4.24 |
| 2 | Research notebook / journal | §6 |
| 3 | Portfolio analytics | existing risk limits + UI |
| 4 | Discord / Slack webhooks | §6 |
| 5 | Advanced charting overlays | §6 |

---

### Infrastructure (parallel, not a user phase)

| Item | When |
|------|------|
| Postgres + Redis | When &gt;1 API replica or SQLite contention | §4.12 |
| Book snapshot retention | With liquidity replay | §4.4 |

### Nice to have / experimental

Scan filters, mobile table polish, deterministic morning brief, modeled liq heatmap, LLM recap with JSON fact-check — after Phase 2 unless trivial.

---

## 8. Deliverable sections (Phase 8 checklist)

| # | Section | Location in doc |
|---|---------|-----------------|
| 1 | Feature comparison matrix | §3 |
| 2 | Missing features | §3 (MI), §4, §6 |
| 3 | Enhancement opportunities | §4, §6 |
| 4 | UX improvements | §3 UX rows, §7 Immediate #4–6 |
| 5 | Dashboard improvements | §4.3, §4.10, §7 |
| 6 | AI improvements | §4.2, §5 (explain-only) |
| 7 | Intelligence improvements | §4.1, §4.11, lane attribution |
| 8 | Infrastructure improvements | §4.12 |
| 9 | Scalability improvements | §4.12, async scan (exists), snapshot retention |
| 10 | Final prioritized roadmap | §7 (v2 phases) |

---

## 9. Competitive positioning statement

**Downpour Trade AI** should be marketed as:

> *The deterministic alternative to black-box AI trading apps:* every score traceable, NO-TRADE by default, **confidence you can prove** (win rate, profit factor, walk-forward, trade count) — with optional AI that **explains** and **coaches**, never **decides**.

Deeepr wins on **breadth of context** (news, macro narrative, scenarios, Copilot). We win on **provable trust, auditability, replay, and risk honesty**. The v2 roadmap closes the **context and workflow** gap without surrendering the core.

**Product owner review:** 9.2/10 on v1 direction; v2 incorporates Trust Layer, Replay, Engine Health, Lifecycle, Heatmap, Scan rejections, Compare, Coach, and lane encyclopedia — plus explicit deferrals (globe, community, strategy builder, paper trading, unverified whales).

---

## 10. Appendix — Quick reference links

- Deeepr.ai: https://deeepr.ai/
- CoinGlass liquidation heatmap docs: https://docs.coinglass.com/reference/liquidation-heatmap
- TradingView crypto screener: https://www.tradingview.com/support/solutions/43000718742-crypto-coins-screener-discover-hidden-gems/
- Downpour glossary (live): `/glossary` on deployed web app

---

*Document owner: Product / Engineering. Review quarterly after competitor releases and calibration results.*
