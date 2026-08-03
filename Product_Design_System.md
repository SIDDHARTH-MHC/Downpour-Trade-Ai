# Downpour Trade AI — Product Design System

**Version:** 1.0  
**Date:** 2026-08-04  
**Scope:** Frontend visual & interaction language only. All data from existing `web/lib/api.ts` contracts.

**Related:** [UI_UX_Audit.md](./UI_UX_Audit.md) · [Application_Architecture.md](./Application_Architecture.md) · [Component_Inventory.md](./Component_Inventory.md) · [Frontend_Redesign_Roadmap.md](./Frontend_Redesign_Roadmap.md)

---

## 1. Scores

| | Score (/10) | Notes |
|---|-------------|--------|
| **Current UI** | **4.2** | See audit — admin-template feel, no tokens/icons/charts |
| **Target UI (v2 workstation)** | **8.5** | Institutional calm, data-dense, keyboard-first; not crypto-casino |
| **Stretch (v3)** | **9.0** | Configurable workspaces, light theme, advanced table/chart polish |

---

## 2. Design principles

1. **Institutional, never flashy** — No neon gradients, no “moon” aesthetics. Trust through clarity.
2. **Explainable by default** — Every signal surface links to evidence, calibration, or engine docs.
3. **Summary → detail → depth** — Progressive disclosure; hero metrics above the fold.
4. **One system, zero one-offs** — No component-specific color hacks; use tokens + variants.
5. **Keyboard-first** — Command palette + shortcuts for power users (Linear/Raycast).
6. **Data-dense but calm** — Bloomberg density with Linear spacing discipline.
7. **Dark-first** — Professional terminal default; light theme phase 2.
8. **Preserve function** — Redesign presentation only; every existing route and API field remains reachable.

---

## 3. Typography system

### Font families

| Token | Stack | Use |
|-------|--------|-----|
| `--font-sans` | **Geist Sans**, `ui-sans-serif`, fallback | All UI copy |
| `--font-mono` | **Geist Mono**, `ui-monospace` | Prices, levels, timestamps, evidence lines |

Load via `next/font` (self-hosted, no layout shift).

### Type scale (rem / line-height)

| Token | Size | Weight | Line | Use |
|-------|------|--------|------|-----|
| `display-lg` | 2.25rem | 600 | 1.1 | Dashboard hero (actionable count) |
| `display-sm` | 1.75rem | 600 | 1.15 | Pair hero action (LONG/SHORT/NO_TRADE) |
| `heading-1` | 1.5rem | 600 | 1.25 | Page titles (module headers) |
| `heading-2` | 1.125rem | 600 | 1.3 | Section titles |
| `heading-3` | 0.875rem | 600 | 1.35 | Card titles, table group headers |
| `body` | 0.875rem | 400 | 1.5 | Default body (14px) |
| `body-sm` | 0.8125rem | 400 | 1.45 | Secondary copy |
| `caption` | 0.75rem | 400 | 1.4 | Stamps, meta, disclaimers |
| `mono-sm` | 0.8125rem | 400 | 1.4 | Entry/SL/TP, bucket IDs |

Letter-spacing: `-0.02em` on display only. **Never** use more than 3 weights (400, 500, 600).

---

## 4. Spacing & grid

### Spacing scale (4px base)

Use Tailwind spacing as canonical: `1=4px`, `2=8px`, `3=12px`, `4=16px`, `5=20px`, `6=24px`, `8=32px`, `10=40px`, `12=48px`, `16=64px`.

| Context | Rule |
|---------|------|
| Card padding | `p-4` (compact) / `p-6` (comfortable) |
| Section gap | `gap-6` between major blocks |
| Inline control gap | `gap-2` |
| Page gutter | `px-4 lg:px-6` inside shell content |
| Max content width | **None** for shell main (fluid); prose docs `max-w-3xl` |

### Grid

- **12-column** fluid grid in main workspace (`grid-cols-12`).
- Dashboard: row 1 = 12 KPI tiles; row 2 = 8 table + 4 sidebar widgets.
- Pair: 12-col with optional 3-col right rail (xl+).

---

## 5. Radius & elevation

| Token | Value | Use |
|-------|-------|-----|
| `radius-sm` | 6px | Badges, chips |
| `radius-md` | 8px | Buttons, inputs |
| `radius-lg` | 12px | Cards, dropdowns |
| `radius-xl` | 16px | Command palette, modals |

| Elevation | CSS | Use |
|-----------|-----|-----|
| `elevation-0` | border only | Default panels |
| `elevation-1` | `shadow-sm` | Popovers |
| `elevation-2` | `shadow-md` | Command palette |
| `elevation-3` | `shadow-lg` | Dialogs (rare) |

Prefer **border + subtle bg** over heavy shadows (Vercel/Linear style).

---

## 6. Color system

### Semantic tokens (dark theme — default)

```css
/* Canvas & surfaces */
--background:        222 47% 4%;    /* #090b10 */
--surface:           222 40% 6%;    /* #0f1218 */
--surface-elevated:  220 35% 9%;    /* #141922 */
--border-subtle:     220 25% 14%;
--border-default:    220 20% 20%;

/* Text */
--foreground:        210 40% 96%;
--muted-foreground:  215 16% 57%;

/* Brand & accent */
--primary:           199 89% 48%;    /* cyan — links, focus */
--primary-foreground: 222 47% 4%;

/* Trading semantics */
--positive:          142 71% 45%;   /* LONG, OK */
--negative:          0 84% 60%;     /* SHORT, error */
--warning:           38 92% 50%;
--neutral-signal:    215 16% 47%;   /* NO_TRADE */

/* Lanes (fixed — never reuse for unrelated UI) */
--lane-technical:    217 91% 60%;
--lane-flow:         263 70% 58%;
--lane-structure:    38 92% 50%;

/* Trust / calibration */
--trust-highlight:   199 80% 40%;   /* subtle border on trust panels */
```

Map to shadcn HSL variables (`background`, `foreground`, `card`, `muted`, `destructive`, etc.).

### Light theme (phase 2)

Invert surfaces; keep `--positive` / `--negative` hue; re-verify **WCAG AA** for `muted-foreground` on `surface` (min 4.5:1).

### Usage rules

- **LONG/SHORT/NO_TRADE** only on verdict chips, hero, heatmap cells — not random buttons.
- **Lane colors** only in lane bars, attribution, lane tab icons.
- **No purple/pink gradients**; no pulsing “live” badges except scan-in-progress (amber, subtle).

---

## 7. Icon system

**Library:** [Lucide React](https://lucide.dev/) — **only** Lucide.

| Size | px | Context |
|------|-----|---------|
| `icon-xs` | 14 | Inline with caption |
| `icon-sm` | 16 | Buttons, table actions |
| `icon-md` | 20 | Sidebar nav |
| `icon-lg` | 24 | Empty states |

`strokeWidth={1.5}` default. Filled icons **not** used (except Lucide filled variants if needed consistently).

### Nav icon map (examples)

| Module | Icon |
|--------|------|
| Command | `Command` |
| Dashboard | `LayoutDashboard` |
| Markets / Pair | `LineChart` |
| Heatmap | `Grid3x3` |
| Portfolio | `PieChart` |
| History | `History` |
| Research (Context) | `Newspaper` |
| Engine | `Cpu` |
| Health | `Activity` |
| Settings | `Settings` |

---

## 8. Component system (shadcn + Radix)

**Stack:** shadcn/ui components copied into `web/components/ui/*`, built on Radix primitives.

### Core primitives to install first

Button, Input, Label, Textarea, Select, Tabs, Dialog, DropdownMenu, Tooltip, Popover, Command (cmdk), Sheet, ScrollArea, Separator, Badge, Card, Skeleton, Toast (Sonner), Table (styled base for TanStack).

### Variant API (CVA)

Every interactive component exposes: `variant`, `size`, `density` (`compact` | `comfortable`).

**Forbidden:** Raw `className="rounded bg-sky-600..."` on pages — use `<Button variant="default">`.

### Card variants

| Variant | Use |
|---------|-----|
| `default` | Standard panel |
| `ghost` | Nested inside another card |
| `trust` | Trust / calibration (left accent border) |
| `signal` | Verdict hero (border tinted by action) |
| `context` | News/macro — labeled “Context only” |

### Status indicators

| State | Visual |
|-------|--------|
| OK | `dot-positive` 8px circle + caption |
| Degraded | `dot-warning` |
| Error | `dot-negative` |
| Unknown | `dot-muted` pulse skeleton |

---

## 9. Chart strategy

| Visualization | Library | Data source (existing API) |
|---------------|---------|----------------------------|
| Pair price + levels | **TradingView Lightweight Charts** | OHLCV: optional future endpoint OR client fetch Binance public klines **read-only** — *if added without backend change, use only public REST from browser*; **preferred v1:** levels on static last price line from `analyze.trade_plan` + structure values |
| Confidence history | **Recharts** | `confidenceHistory` |
| Calibration buckets | **Recharts** bar | `calibrateStatus` |
| Attribution bars | Design-system CSS or Recharts | `verdict.attribution` |
| Correlation matrix | **ECharts** heatmap or CSS grid + scale | `correlationMatrix` |
| Scanner heatmap | CSS + color scale | `scan.results` |
| Portfolio heat | Radial / gauge (Recharts) | `portfolioAnalytics` |
| Engine health | Status tiles (no chart) | `engineStatus` |

**Rule:** Lightweight Charts for **price** only; Recharts for **metrics**; avoid loading both on same route until lazy-loaded.

---

## 10. Table strategy

**Library:** [@tanstack/react-table](https://tanstack.com/table) + shadcn DataTable pattern.

| Feature | Priority |
|---------|----------|
| Sort | P0 |
| Column filter | P0 |
| Sticky header | P0 |
| Row click → pair | P0 |
| Density toggle | P1 |
| Column resize | P2 |
| Pinned columns (symbol) | P1 |
| Context menu (open, compare, pin) | P2 |
| Bulk export CSV | P3 |

Apply to: Dashboard scan table, History, Flows, Backtests buckets, Portfolio positions.

---

## 11. Motion guidelines

**Library:** `framer-motion` — **micro only**.

| Allowed | Duration | Easing |
|---------|----------|--------|
| Sidebar collapse | 200ms | ease-out |
| Tab panel fade | 150ms | ease-out |
| Command palette open | 150ms | spring subtle |
| Number tick (score) | 300ms | ease-out |
| Skeleton → content | 150ms opacity | |
| Toast enter/exit | 200ms | |

**Forbidden:** Parallax, page transitions, bouncing buttons, confetti, crypto “pulse” on prices.

**Reduced motion:** `@media (prefers-reduced-motion: reduce)` → disable all transforms; instant state changes.

---

## 12. States

### Loading

- Route-level: shell stays visible; content area skeletons match final layout.
- Pair hero: skeleton for action + score before analyze returns.

### Empty

- Icon (Lucide) + title + one sentence + primary action (e.g. “Run calibration”).
- Link to `/engine` or glossary where relevant.

### Error

- Sonner toast for transient; inline `Alert` variant destructive for block errors.
- **Remove** `alert()` browser dialogs.

### Focus

- Visible `ring-2 ring-primary ring-offset-2 ring-offset-background` on all interactive elements (shadcn default).

---

## 13. Data visualization language

| Concept | Visual treatment |
|---------|------------------|
| **Confidence** | Tier badge (HIGH/MOD/LOW/INSUFFICIENT) + win rate + n + WF pass icon |
| **Trust** | Dedicated card with 8-metric grid; WF pass/fail prominent |
| **Lanes** | Horizontal signed bar -100..+100, lane color, evidence in collapsible |
| **Regime** | Pill + tradeable dot; SHOCK = muted red border on hero |
| **Replay** | Vertical timeline with step numbers, category icons |
| **Heatmap** | Cell background = action hue; opacity = \|score\| |
| **Risk** | SL/TP distance in R multiples; portfolio heat gauge |

---

## 14. Responsive strategy

**Desktop-first** (1280px+ optimal).

| Breakpoint | Shell behavior |
|------------|----------------|
| `< lg` | Sidebar → Sheet overlay; bottom nav (Dashboard, Search, Watchlist, More) |
| `lg–xl` | Collapsed sidebar (icons only) |
| `≥ xl` | Full sidebar + optional pair right rail |

Pair page mobile: hero sticky; tabs scroll horizontal; chart fixed height 240px.

---

## 15. Accessibility strategy (WCAG AA target)

- Semantic landmarks: `nav`, `main`, `aside`, `header`.
- Skip link: “Skip to workspace”.
- Command palette: focus trap, `aria-activedescendant`.
- Tables: `scope` on headers; sort buttons labeled.
- Charts: text alternative summary under chart (verdict action + levels list).
- Color: never rely on color alone — pair icons/text with LONG/SHORT labels.
- Test: axe in CI on key routes (dashboard, pair).

---

## 16. GitHub & product inspiration

See [Frontend_Redesign_Roadmap.md](./Frontend_Redesign_Roadmap.md) § References.

**Study for:** layout density (CoinGlass), command palette (Linear), status (Grafana), trust (Stripe), calm dark (Vercel).

**Do not copy:** Magic UI / Aceternity heavy motion; crypto casino dashboards.

---

## 17. Workspace concept (visual)

| Workspace | Density | Default module |
|-----------|---------|----------------|
| **Trading** | High | Dashboard + heatmap |
| **Research** | Medium | Pair + context + engine |
| **Portfolio** | Medium | Portfolio + scenarios |
| **Compact** | Max | Tables only, collapsed sidebar |
| **News** | Medium | Context feed + macro |

Persist layout preference in `localStorage` (`downpour.workspace.v1`) — no backend.

---

## 18. Command palette & keyboard (summary)

Full spec in [Application_Architecture.md](./Application_Architecture.md).

- **⌘K / Ctrl+K:** Command palette
- **/** focus palette search
- **G then D/P/H:** Go dashboard / portfolio / history
- **⌘B:** Toggle sidebar

---

*This document is the single source of truth for visual implementation. Update version when tokens change.*
