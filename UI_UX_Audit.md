# Downpour Trade AI — UI/UX Audit

**Date:** 2026-08-04  
**Scope:** Frontend only (`web/`). No backend, API, or business-logic changes in this document.  
**Stack today:** Next.js 14, React 18, Tailwind 3, SWR. **No** icon library, **no** chart library, **no** component kit (shadcn/Radix/Mantine).

---

## 1. Current UI score

| Dimension | Score (/10) | Summary |
|-----------|-------------|---------|
| **Overall product UI** | **4.2** | Functional MVP dashboard; reads as internal admin tool, not institutional trading product. |
| Visual polish | 3.8 | Ad-hoc Tailwind; no design tokens beyond 6 colors. |
| Information hierarchy | 4.0 | Page titles repeat pattern; pair page is long scroll of equal-weight cards. |
| Navigation & IA | 4.5 | AppNav improved vs flat list; still page-centric, no app shell. |
| Data visualization | 3.0 | Bars and tables only; no price charts; heatmap is CSS grid. |
| Consistency | 4.5 | Shared `.card` helps; buttons/inputs vary per page. |
| Responsiveness | 5.5 | Tailwind breakpoints used; pair page overwhelming on mobile. |
| Accessibility | 4.0 | Some `aria-expanded`; no skip links, focus rings inconsistent, contrast OK on dark. |
| Performance (perceived) | 6.0 | Small bundle; skeleton exists; no optimistic UI or command palette. |
| Delight / premium feel | 3.5 | Little motion, no iconography, no empty-state illustration system. |

**Weighted overall: 4.2 / 10** — appropriate for a shipped alpha, not for “Bloomberg × TradingView × Linear” positioning.

---

## 2. Page-by-page review

Scores: **1** = broken/unusable · **5** = acceptable MVP · **10** = best-in-class reference quality.

| Page | Route | Score | Why |
|------|-------|-------|-----|
| **Dashboard** | `/` | **5.0** | Clear scan table + explain panel + watchlist, but no at-a-glance KPI strip (regime, actionable count, portfolio heat, last scan). Title + table feels like CRUD admin. |
| **Pair detail** | `/pair/[symbol]` | **4.5** | Rich data (trust, lanes, replay, news) but **flat vertical stack** ~15 sections; no tabs/sticky summary; duplicate lifecycle vs API; overwhelming on mobile. |
| **History** | `/history` | **4.0** | Table list; weak filters/sort; confidence chart secondary; no density toggle. |
| **Heatmap** | `/heatmap` | **5.0** | Simple grid works; not a true heatmap (no score gradient, no legend, no sector grouping). |
| **Compare** | `/compare` | **4.5** | Raw inputs + 2 cards; no shared axis for lanes; no trust side-by-side in UI. |
| **Correlation** | `/correlation` | **4.0** | Text/table; misnamed “matrix” in product terms; no visual matrix/cells. |
| **Scenarios** | `/scenarios` | **4.0** | Form + result list; fine for MVP; no risk summary card. |
| **Context feed** | `/news` | **4.5** | Tabs + articles; sentiment badges ad hoc; no reading layout typography. |
| **Funding** | `/flows` | **4.5** | Multi-symbol fetch; table-only; CoinGlass-style compare missing visually. |
| **Macro** | `/macro` | **4.0** | Metrics + ETF stub; no sparklines or regime linkage visual. |
| **Engine docs** | `/engine` | **6.0** | Best content hierarchy on static docs; still unstyled prose blocks. |
| **Backtests / calibration** | `/backtests` | **5.0** | Summary dl + table; good honesty; `alert()` for errors; no progress component. |
| **Engine health** | `/status` | **5.0** | Grid of checks; Grafana-style status dots/timeline would elevate. |
| **Alerts** | `/alerts` | **3.5** | Native inputs/buttons; no validation UX; forms feel prototype. |
| **Coach** | `/coach` | **4.0** | Chat-like without message UI; markdown blob; no thread layout. |
| **Notebook** | `/notebook` | **3.5** | Basic CRUD; no rich text, tags UI weak. |
| **Portfolio** | `/portfolio` | **4.5** | Single equity input + table; heat % buried; no gauge. |
| **Integrations** | `/integrations` | **4.0** | Two URL fields; minimal feedback on save. |
| **Glossary** | `/glossary` | **5.5** | Readable; consistent with engine page. |

**Global chrome:** Layout header (`web/app/layout.tsx`) — **4.5**. Logo + top nav; no sidebar, search, user menu, or market status strip.

---

## 3. Biggest UX problems

1. **No application shell** — Pages feel like separate routes in a template, not one trading workstation (Linear/Vercel app model).
2. **Dashboard doesn’t answer trader questions** — Missing hero metrics: actionable signals, dominant regime, BTC gate, portfolio heat, calibration freshness, scan progress.
3. **Pair page cognitive overload** — Everything same visual weight; trust/verdict should be sticky hero; context (news/coach) should be secondary panel/tabs.
4. **No global search or command palette** — 19 routes hidden behind “More”; no ⌘K jump to symbol or page.
5. **Weak wayfinding** — No breadcrumbs, no “recent pairs,” no pinned symbols in nav.
6. **Forms and actions inconsistent** — Mix of `alert()`, plain buttons, unlabeled loading states.
7. **No charting** — Professional traders expect price + levels; overlays are a monospace list (`ChartOverlaysPanel`).
8. **Tables are bare** — No sort, filter, column resize, sticky header, or row actions.
9. **Empty states are one-line text** — Missed onboarding and trust-building copy.
10. **Mobile: pair page unusable at depth** — No collapsible sections or bottom nav.

---

## 4. Biggest visual problems

1. **Typography** — System UI stack only; no scale (display/title/body/caption); headings all `text-2xl font-bold`.
2. **Color system** — Six Tailwind extends (`surface`, `panel`, `border`, `long`, `short`, `muted`); ad hoc `sky-*`, `slate-*`, `amber/violet` per component.
3. **No icons** — Zero visual anchors for nav, status, lanes, or actions.
4. **Cards** — Single `.card` class; trust card uses one-off `border-sky-900/50 bg-slate-900/40`.
5. **Spacing** — Mostly `space-y-4` and `p-4`; no 4/8px systematic scale.
6. **Elevation** — `shadow-lg` on all cards; no layered depth language.
7. **Buttons/inputs** — Inline Tailwind per page; no primary/secondary/ghost/destructive variants.
8. **Data density** — Either sparse (macro) or dense text walls (lane evidence) without progressive disclosure.
9. **Brand** — Sky blue links only; no logo mark, no motion, no “institutional calm.”
10. **Light theme** — Not supported (dark only).

---

## 5. Design system proposal

Build **`web/design-system/`** (tokens + docs) and **`globals.css` CSS variables** consumed by Tailwind.

### Typography

| Token | Use | Suggestion |
|-------|-----|------------|
| `font-sans` | UI | **Inter** or **Geist Sans** (Vercel) |
| `font-mono` | Prices, levels, evidence | **Geist Mono** or **IBM Plex Mono** |
| `text-display` | Dashboard hero | 32–40px / semibold / -0.02em |
| `text-h1` | Page title | 24px / semibold |
| `text-h2` | Section | 18px / medium |
| `text-body` | Default | 14px / regular / 1.5 line-height |
| `text-caption` | Meta, stamps | 12px / muted |

### Spacing scale (4px base)

`0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16` → map to `space-1` … `space-16` (Tailwind defaults align).

### Radius

| Token | Value | Use |
|-------|-------|-----|
| `radius-sm` | 6px | Chips, badges |
| `radius-md` | 8px | Inputs, buttons |
| `radius-lg` | 12px | Cards |
| `radius-xl` | 16px | Modals, command palette |

### Elevation

| Level | Shadow | Use |
|-------|--------|-----|
| `elevation-0` | none | Flat panels |
| `elevation-1` | subtle border | Default card |
| `elevation-2` | soft shadow | Dropdowns, popovers |
| `elevation-3` | stronger | Command palette, dialogs |

### Color palette (dark primary, light optional phase 2)

**Dark (default — institutional)**

| Token | Role | Example hex |
|-------|------|-------------|
| `bg-canvas` | App background | `#090b10` |
| `bg-surface` | Panels | `#0f1218` |
| `bg-elevated` | Cards | `#141922` |
| `border-subtle` | Hairlines | `#1e2633` |
| `border-default` | | `#2a3544` |
| `text-primary` | | `#e8edf4` |
| `text-secondary` | | `#94a3b8` |
| `accent` | Brand / links | `#38bdf8` → shift to cooler cyan for premium |
| `positive` | Long / OK | `#22c55e` |
| `negative` | Short / error | `#ef4444` |
| `warning` | Degraded | `#f59e0b` |
| `lane-technical` | | `#3b82f6` |
| `lane-flow` | | `#8b5cf6` |
| `lane-structure` | | `#f59e0b` |

**Light theme (phase 2):** Same semantic tokens; invert backgrounds; verify WCAG AA contrast for `text-secondary` on `bg-surface`.

### Components (semantic variants)

- **Card:** `default` | `highlight` (trust) | `muted` (context-only disclaimer)
- **Button:** `primary` | `secondary` | `ghost` | `destructive` | `icon`
- **Badge:** verdict (LONG/SHORT/NO_TRADE), regime, confidence tier, sentiment
- **Table:** sticky header, zebra optional, row hover, compact/comfortable density
- **Tabs:** pair page sections (Signal | Lanes | Plan | Context | Replay)
- **Skeleton:** match card layouts, not generic bars only
- **Empty state:** icon + title + action + doc link
- **Toast:** replace `alert()` for calibrate/errors

Implement via **shadcn/ui** (copy-paste, Tailwind-native) on **Radix** primitives.

---

## 6. Icon library recommendation

**Primary: [Lucide React](https://lucide.dev/)**

| Criterion | Lucide | Heroicons | Tabler | Phosphor |
|-----------|--------|-----------|--------|----------|
| Consistency | Excellent single stroke | Good | Good | Multiple weights (risk of mix) |
| Coverage | Very large | Smaller | Large | Large |
| React/Next | First-class | Good | Good | Good |
| Trading fit | TrendingUp, Activity, Shield | Similar | Similar | Similar |
| Bundle | Tree-shakeable | Tree-shakeable | Tree-shakeable | Tree-shakeable |

**Rule:** Lucide only; 16px inline, 20px nav, 24px empty states; `stroke-width={1.5}` default.

---

## 7. Component library recommendation

**Recommended stack**

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Primitives | **Radix UI** (via shadcn) | Accessibility, focus trap, dialogs, tabs |
| Components | **shadcn/ui** | Tailwind + ownership; matches Vercel/Linear ecosystem |
| Utilities | **class-variance-authority**, **tailwind-merge**, **clsx** | Variant API |
| Command palette | **cmdk** | Raycast/Linear pattern |
| Toasts | **sonner** or shadcn toast | Non-blocking errors |
| Forms | **react-hook-form** + shadcn Form | Alerts/integrations/scenarios |

**Not recommended as primary:** Mantine (second theme system), Aceternity/Magic UI (motion-heavy, off-brand for institutional).

**Optional later:** Tremor for metric cards only if not building custom on shadcn.

---

## 8. Chart library recommendation

| Use case | Library | Why |
|----------|---------|-----|
| **Price + levels + future replay** | **[TradingView Lightweight Charts](https://www.tradingview.com/lightweight-charts/)** | Industry standard feel; performant canvas; horizontal lines for SL/TP/POC |
| **Confidence history, calibration buckets** | **[Recharts](https://recharts.org/)** or **Apache ECharts** | Time series + bar charts; React-friendly (Recharts) vs power (ECharts) |
| **Attribution / lane bars** | **Custom CSS** or Recharts horizontal bars | Already linear data; keep in design system colors |
| **Correlation “matrix”** | **ECharts heatmap** or CSS grid with color scale | Match product name visually |
| **Scanner heatmap** | Enhanced CSS grid + score → color interpolation | No chart lib required initially |
| **Portfolio heat gauge** | Radial bar (Recharts) or custom SVG | Single metric emphasis |

**Default pick:** Lightweight Charts (pair/dashboard) + Recharts (analytics pages). Avoid Nivo (heavier) unless React Flow needed for replay graph (probably not — timeline UI is enough).

---

## 9. GitHub repositories worth studying (patterns, not copy)

| Repo | Learn |
|------|--------|
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | Component patterns, dark theme |
| [tremorlabs/tremor](https://github.com/tremorlabs/tremor) | Metric dashboards, KPI rows |
| [calcom/cal.com](https://github.com/calcom/cal.com) | App shell, settings IA |
| [vercel/examples](https://github.com/vercel/examples) | Geist, layout |
| [tradingview/lightweight-charts](https://github.com/tradingview/lightweight-charts) | Chart integration examples |
| [papermark/paper](https://github.com/mfts/papermark) | shadcn dashboard polish |
| [baptisteArno/typebot.io](https://github.com/baptisteArno/typebot.io) | Sidebar + content (Linear-like) |
| [Kiranism/next-shadcn-dashboard-starter](https://github.com/Kiranism/next-shadcn-dashboard-starter) | Table + filter patterns (adapt, don’t clone aesthetic) |

---

## 10. Inspiration references (public)

| Product | URL | Relevant patterns |
|---------|-----|-------------------|
| TradingView | https://www.tradingview.com/ | Watchlist + chart + symbol header; dense but clear hierarchy |
| CoinGlass | https://www.coinglass.com/ | Funding tables, heat colors, dark terminal aesthetic |
| Linear | https://linear.app/ | Sidebar, command menu, calm dark UI |
| Vercel Dashboard | https://vercel.com/dashboard | KPI cards, status pills, Geist typography |
| GitHub | https://github.com/ | Tabbed repo views, sticky headers |
| Raycast | https://www.raycast.com/ | Command palette, keyboard-first |
| Stripe Dashboard | https://dashboard.stripe.com/ | Forms, empty states, trust |
| Grafana | https://grafana.com/ | Status panels (/status page) |
| Glassnode | https://glassnode.com/ | Institutional charts + metrics |
| Tailscale admin | https://login.tailscale.com/admin | Clean technical admin, health states |

*(Screenshots: capture during redesign phase for internal mood board; not embedded here.)*

---

## 11. Prioritized redesign roadmap

### Phase A — Foundation (1–2 weeks)

- Install shadcn + Lucide + CSS variable tokens in `globals.css` / `tailwind.config`
- App shell: **collapsible sidebar** + **top bar** (symbol search placeholder, data stamp, health dot)
- Replace `.card` / buttons / inputs with design-system components
- Standardize **PageHeader** (title, description, actions slot)
- Toast system; remove `alert()`

**No API changes** — same SWR hooks.

### Phase B — Dashboard & pair (2–3 weeks)

- Dashboard **KPI row**: actionable count, last scan, dominant regime, portfolio heat (from existing APIs)
- **Pair layout**: sticky verdict strip; tabs (Overview | Lanes | Plan | Context | Audit)
- Integrate **Lightweight Charts** with levels from existing verdict JSON (read-only)
- Trust card visual hierarchy (primary metric: confidence + win rate)

### Phase C — Data views (1–2 weeks)

- Table kit: sort/filter on history, flows, backtests
- Heatmap v2: score gradient + legend
- Correlation visual grid
- Confidence history chart (Recharts)

### Phase D — Power UX (1–2 weeks)

- **Command palette** (⌘K): pages + “Analyze BTC/USDT” deep link
- Keyboard shortcuts doc in glossary
- Watchlist in sidebar (localStorage preserved)
- Improved empty/loading/error states per page

### Phase E — Polish & a11y (1 week)

- Focus rings, skip link, aria labels on nav
- `prefers-reduced-motion`
- Light theme token prep (optional ship)
- Mobile: bottom nav for top 4 destinations + collapsible pair sections

### Phase F — Delight (ongoing)

- Subtle transitions (150ms) on hover/tab
- Scan-complete toast
- Regime-colored ambient border on dashboard (subtle)

---

## 12. Estimated effort

| Phase | Engineering (frontend) | Design (tokens/mockups) |
|-------|------------------------|-------------------------|
| A Foundation | 5–8 days | 2–3 days |
| B Dashboard + Pair | 10–15 days | 4–5 days |
| C Data views | 6–10 days | 2–3 days |
| D Power UX | 5–8 days | 2 days |
| E A11y/polish | 3–5 days | 1–2 days |
| **Total to “premium v1”** | **~29–46 days** (1 dev) | **~11–15 days** |

Parallel design + dev can compress calendar time to **6–8 weeks**.

---

## 13. Mockup descriptions (major pages)

### Dashboard `/`

- **Top:** 4–6 KPI tiles — Actionable signals (green/red count), Last scan time + progress, BTC regime pill, Portfolio heat (link), Calibration status (pass/fail dot).
- **Center-left (70%):** Enhanced scan table — sortable, confidence column, quick filter LONG/SHORT/NO_TRADE.
- **Center-right (30%):** Scan rejection donut (from `scan_report`) + mini heatmap (5×4 grid).
- **Bottom:** Watchlist strip with sparkline placeholders (future) or score chips.

### Pair `/pair/[symbol]`

- **Sticky header:** Symbol, price (from verdict mid if available), LARGE action chip, score, regime, confidence one-liner.
- **Row 2:** Lightweight chart with entry/SL/TP/POC lines (toggle).
- **Tabs:** Overview (trust + attribution + reasons) | Lanes | Trade plan | Context (news + macro link) | Replay & lifecycle.
- **Right rail (desktop):** Copilot + coach collapsed accordions.

### History `/history`

- Filter bar: symbol, outcome, action, date range (client-side on loaded data).
- Split: table + confidence timeline chart.

### Heatmap `/heatmap`

- Legend: NO_TRADE → LONG gradient by |score|.
- Group sort: actionable first.

### Compare `/compare`

- Two-column synchronized lane bars; trust metrics row; shared regime comparison.

### Backtests `/backtests`

- Hero: last calibrated, WF pass badge, OOS trade count.
- Bar chart per bucket + table below.
- Progress stepper when `running`.

### Status `/status`

- Grafana-style: green/amber/red tiles, last check time, expandable detail.

### Context `/news`

- Two-column: filters left, timeline right; card per headline with sentiment + source icon.

*(Other pages: apply **PageHeader** + single primary card + table pattern for consistency.)*

---

## 14. Components to redesign

| Component | File | Priority |
|-----------|------|----------|
| App shell / nav | `layout.tsx`, `AppNav.tsx` | P0 |
| Page header | *new* `PageHeader.tsx` | P0 |
| Card / panel | `globals.css` → shadcn Card | P0 |
| Button / Input / Select | scattered pages | P0 |
| PairTable | `PairTable.tsx` | P0 |
| VerdictCard | `VerdictCard.tsx` | P0 |
| TrustCard | `TrustCard.tsx` | P0 |
| LanePanel | `LanePanel.tsx` | P1 |
| SignalAttribution | `SignalAttribution.tsx` | P1 |
| ScannerHeatmap | `ScannerHeatmap.tsx` | P1 |
| ScoreGauge | `ScoreGauge.tsx` | P1 |
| TradePlanBox | `TradePlanBox.tsx` | P1 |
| ChartOverlaysPanel | `ChartOverlaysPanel.tsx` → chart integration | P0 |
| ConfidenceHistoryChart | `ConfidenceHistoryChart.tsx` | P1 |
| ReplayLifecycle | `ReplayLifecycle.tsx` | P1 |
| ScanExplainPanel | `ScanExplainPanel.tsx` | P1 |
| WatchlistPanel | `WatchlistPanel.tsx` | P1 |
| NewsContextPanel | `NewsContextPanel.tsx` | P2 |
| CopilotPanel / CoachPanel | `CopilotPanel.tsx`, `CoachPanel.tsx` | P2 |
| DisclaimerFooter / DataStamp / Loading / Error | `DisclaimerFooter.tsx` | P0 |
| RegimeBadge | `RegimeBadge.tsx` | P1 |
| All page files under `app/**/page.tsx` | Layout composition only | P1 |

---

## UX feature evaluation (current vs target)

| Feature | Current | Target |
|---------|---------|--------|
| Search | None | Command palette + symbol jump |
| Filters | Minimal | Tables + history |
| Sorting | None | Client/server where API already supports |
| Keyboard shortcuts | None | ⌘K, ? help |
| Command palette | None | cmdk |
| Pinned watchlist | localStorage panel | Sidebar section |
| Context menus | None | Row actions on tables |
| Split panes | None | Pair: chart + tabs |
| Breadcrumbs | None | Shell: Market > BTC/USDT |
| Sticky headers | None | Pair verdict strip |
| Notifications | None | Toasts on scan/alerts |
| Accessibility | Partial | WCAG AA pass on shell + pair |

---

## Frontend performance notes

| Finding | Detail |
|---------|--------|
| Bundle size | **Small** (~SWR + Next only) — room for charts/icons without panic |
| Re-renders | SWR fine; pair page many panels = one analyze fetch (good) |
| Duplicate requests | Watchlist batch + dashboard scan separate (acceptable) |
| Hydration | Mostly client pages; low risk |
| Perceived speed | Add skeletons per section; stagger pair tab loading |

---

## Critical rules compliance (this audit)

- No backend changes proposed in implementation phase beyond what already exists.
- All redesign consumes **existing** `web/lib/api.ts` contracts.
- Every feature preserved; presentation and IA improve discoverability.

---

## Next step (when approved)

1. Approve design tokens + shell wireframe.  
2. Phase A PR: shadcn init + AppShell only (visual parity on 2 pages).  
3. Phase B: Dashboard + Pair (highest ROI).

*End of audit.*
