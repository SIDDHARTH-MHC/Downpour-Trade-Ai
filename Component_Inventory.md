# Downpour Trade AI — Component Inventory

**Version:** 1.0  
**Date:** 2026-08-04  
**Purpose:** Map existing UI → target design system. **No API or logic changes** — composition and presentation only.

---

## 1. Inventory summary

| Category | Existing | Target (new/refactor) | shadcn base |
|----------|----------|------------------------|-------------|
| Shell | 1 (`AppNav`) | 5 | Sheet, ScrollArea |
| Primitives | 0 | ~20 in `ui/` | Full shadcn set |
| Domain | 20 | 20 refactored | Card, Table, Tabs |
| Pages | 19 | 19 layouts only | — |

---

## 2. Shell components

| ID | Current | Target component | Priority | Notes |
|----|---------|------------------|----------|-------|
| SH-01 | `AppNav.tsx` | **Deprecate** → `SidebarNav` | P0 | Move links to `lib/navigation.ts` |
| SH-02 | — | `AppShell` | P0 | Layout grid sidebar + main |
| SH-03 | — | `TopBar` | P0 | Breadcrumbs, search trigger |
| SH-04 | — | `StatusBar` | P1 | Health, scan, stamp |
| SH-05 | — | `MobileNav` | P1 | Bottom bar lg:hidden |
| SH-06 | — | `CommandPalette` | P0 | cmdk |
| SH-07 | — | `ShortcutsDialog` | P2 | ? key |
| SH-08 | `layout.tsx` | `RootLayout` + providers | P0 | Fonts, theme |

---

## 3. shadcn/ui primitives (`components/ui/`)

Install in Phase A — **do not customize per page**.

| Component | Use in product |
|-----------|----------------|
| Button | All actions |
| Input, Textarea, Label | Alerts, notebook, scenarios, integrations |
| Select | TF selectors, filters |
| Tabs | Pair module, news categories |
| Card, CardHeader, CardTitle, CardContent | Replace `.card` |
| Badge | Regime, verdict, sentiment |
| Dialog | Confirm delete alert/journal |
| DropdownMenu | Row actions, workspace switcher |
| Popover | TF picker, column filters |
| Tooltip | Icon buttons, truncated confidence |
| Command | Palette |
| Sheet | Mobile sidebar |
| ScrollArea | Sidebar, long evidence |
| Separator | Section splits |
| Skeleton | Loading states |
| Sonner (toast) | Errors, saves |
| Alert | Inline block errors |
| Table | Base for TanStack |

---

## 4. Shared domain components (refactor)

| ID | File | Target name | Changes | API deps |
|----|------|-------------|---------|----------|
| DC-01 | `DisclaimerFooter.tsx` | `LegalFooter` + **`DataStamp`** + **`LoadingSkeleton`** + **`ErrorAlert`** | Split; use shadcn Alert/Skeleton | — |
| DC-02 | `RegimeBadge.tsx` | `RegimeBadge` | Token colors; Lucide icon | `regime.name`, `tradeable` |
| DC-03 | `VerdictCard.tsx` | **`SignalHero`** (pair) + `VerdictSummary` (compact) | Hero typography; sticky | `Verdict` |
| DC-04 | `TrustCard.tsx` | `TrustPanel` | Variant `trust`; metric grid | `trust` |
| DC-05 | `TradePlanBox.tsx` | `TradePlanPanel` | Mono prices; R:R prominent | `trade_plan` |
| DC-06 | `ScoreGauge.tsx` | `ScoreGauge` | Motion on value change (optional) | `weighted_score` |
| DC-07 | `SignalAttribution.tsx` | `AttributionChart` | Lane tokens | `attribution`, `lanes` |
| DC-08 | `LanePanel.tsx` | `LaneGrid` / `LaneCard` | Signed bar; collapsible evidence | `lanes` |
| DC-09 | `StructureEventsPanel.tsx` | `StructureEventsList` | Timeline style | `structure_events` |
| DC-10 | `ChartOverlaysPanel.tsx` | **`PriceChart`** + `LevelsLegend` | Lightweight Charts | `verdict`, levels |
| DC-11 | `ConfidenceHistoryChart.tsx` | `ConfidenceTimeline` | Recharts | `confidenceHistory` |
| DC-12 | `ReplayLifecycle.tsx` | `ReplayTimeline` + `LifecycleStepper` | Unified timeline component | `replay_events`, lifecycle |
| DC-13 | `PairTable.tsx` | **`ScanTable`** (TanStack) | Sort, filter, sticky | `scan.results` |
| DC-14 | `ScannerHeatmap.tsx` | `ScannerHeatmap` | Score gradient scale | `scan.results` |
| DC-15 | `ScanExplainPanel.tsx` | `ScanRejectionChart` | Bar/donut from report | `scan_report` |
| DC-16 | `WatchlistPanel.tsx` | `WatchlistStrip` + sidebar pins | Sync pinned store | `analyzeBatch` |
| DC-17 | `NewsContextPanel.tsx` | `ContextNewsFeed` | Reading typography | `contextNews` |
| DC-18 | `LiquiditySnapshotPanel.tsx` | `LiquidityPanel` | Table + walls list | `liquiditySnapshot` |
| DC-19 | `CopilotPanel.tsx` | `ExplainCopilot` | Markdown prose styles | `copilotExplain` |
| DC-20 | `CoachPanel.tsx` | `CoachChat` | Message bubbles (static markdown) | `coachChat` |

---

## 5. Module compositions (new)

| Module | Route | Composed from | New layout only |
|--------|-------|-------------|-----------------|
| M-01 | `/` | KPIRow, ScanTable, ScanRejectionChart, ScannerHeatmap, WatchlistStrip | Yes |
| M-02 | `/pair/[symbol]` | SignalHero, PriceChart, PairTabs (all DC) | Yes |
| M-03 | `/history` | ModuleHeader, HistoryTable, ConfidenceTimeline | Yes |
| M-04 | `/heatmap` | ModuleHeader, ScannerHeatmap (full) | Yes |
| M-05 | `/compare` | ModuleHeader, CompareColumns | Yes |
| M-06 | `/correlation` | ModuleHeader, CorrelationMatrix | Yes |
| M-07 | `/scenarios` | ModuleHeader, ScenarioForm, ResultsList | Yes |
| M-08 | `/news` | ModuleHeader, ContextNewsFeed (full page) | Yes |
| M-09 | `/flows` | ModuleHeader, FundingTable | Yes |
| M-10 | `/macro` | ModuleHeader, MacroMetrics, EtfStubCard | Yes |
| M-11 | `/engine` | ModuleHeader, Prose docs | Yes |
| M-12 | `/backtests` | ModuleHeader, CalibrationKPIs, BucketTable, BucketChart | Yes |
| M-13 | `/status` | ModuleHeader, HealthGrid | Yes |
| M-14 | `/alerts` | ModuleHeader, AlertRuleForm, RulesTable | Yes |
| M-15 | `/coach` | ModuleHeader, CoachChat | Yes |
| M-16 | `/notebook` | ModuleHeader, JournalEditor, JournalList | Yes |
| M-17 | `/portfolio` | ModuleHeader, PortfolioHeatGauge, PositionsTable | Yes |
| M-18 | `/integrations` | ModuleHeader, IntegrationForm | Yes |
| M-19 | `/glossary` | ModuleHeader, Prose | Yes |

---

## 6. New shared building blocks

| Component | Responsibility |
|-----------|----------------|
| `ModuleHeader` | title, description, actions slot, data stamp |
| `KPIRow` | 4–6 metric tiles |
| `MetricTile` | label, value, delta optional, status dot |
| `DataTable` | TanStack wrapper (sort, filter, density) |
| `PairTabs` | Tab state + lazy mount panels |
| `EmptyState` | icon, title, description, action |
| `PageError` | retry button → mutate SWR |
| `VerdictChip` | LONG/SHORT/NO_TRADE (from PairTable — extract) |
| `SentimentBadge` | news (from NewsContextPanel — extract) |
| `Prose` | engine/glossary markdown styling |

---

## 7. Duplication to eliminate

| Issue | Locations | Fix |
|-------|-----------|-----|
| `.card` + one-off borders | Trust, Verdict, many pages | Card variants |
| Button classes `bg-sky-600` | backtests, pair tf, news tabs | Button variants |
| `text-2xl font-bold` h1 | every page | ModuleHeader |
| Sentiment/verdict chips | news, pair table | Shared badges |
| Loading/error | DisclaimerFooter | Standard skeleton/alert |
| TF toggle buttons | pair, watchlist | Segmented control (Tabs) |
| `alert()` | backtests | toast |

---

## 8. Component ↔ API matrix (unchanged)

| API method | Primary components |
|------------|-------------------|
| `scan` | ScanTable, ScannerHeatmap, ScanRejectionChart, KPIRow |
| `analyze` | SignalHero, PriceChart, LaneGrid, TrustPanel, … |
| `analyzeBatch` | WatchlistStrip |
| `confidenceHistory` | ConfidenceTimeline |
| `compare` | CompareColumns |
| `correlationMatrix` | CorrelationMatrix |
| `runScenario` | ScenarioForm |
| `contextNews` | ContextNewsFeed |
| `contextEtf` | EtfStubCard |
| `flowsSnapshot` | FundingTable |
| `macroSnapshot` | MacroMetrics |
| `calibrateStatus` / `startCalibrate` | CalibrationKPIs, BucketTable |
| `engineStatus` | HealthGrid |
| `alertRules` | RulesTable |
| `coachChat` | CoachChat |
| `journalList` / save / delete | JournalList |
| `portfolioAnalytics` | PortfolioHeatGauge |
| `integrationsGet/Save` | IntegrationForm |
| `copilotExplain` | ExplainCopilot |
| `liquiditySnapshot` | LiquidityPanel |
| `history` | HistoryTable |

---

## 9. Dependencies to add (frontend only)

| Package | Purpose |
|---------|---------|
| `@radix-ui/*` | via shadcn |
| `class-variance-authority`, `clsx`, `tailwind-merge` | variants |
| `lucide-react` | icons |
| `cmdk` | command palette |
| `sonner` | toasts |
| `@tanstack/react-table` | tables |
| `lightweight-charts` | pair chart |
| `recharts` | metrics charts |
| `framer-motion` | micro motion (optional phase) |
| `geist` | fonts |

---

## 10. Deprecation plan

| After phase | Remove |
|-------------|--------|
| B | Global `.card` in globals.css (keep alias → Card) |
| B | `AppNav.tsx` |
| C | Inline table markup in pages |
| D | `ChartOverlaysPanel` as list-only (replaced by chart legend) |

---

## 11. Testing checklist (UI)

- [ ] Shell: sidebar collapse persists  
- [ ] Command: navigate to all 19 modules  
- [ ] Pair: all tabs render same data as before  
- [ ] Keyboard shortcuts don’t fire in inputs  
- [ ] axe: 0 critical on `/` and `/pair/BTC/USDT`  
- [ ] Mobile: bottom nav + sheet sidebar  

---

*Inventory updates when components merge or split during implementation.*
