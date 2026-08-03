# Downpour Trade AI — Frontend Application Architecture

**Version:** 1.0  
**Date:** 2026-08-04  
**Constraint:** Zero changes to backend, APIs, engine, or business logic. All modules consume existing `web/lib/api.ts`.

---

## 1. Mental model

```
┌─────────────────────────────────────────────────────────────────┐
│  APPLICATION SHELL (persistent)                                  │
│  ┌──────────┬──────────────────────────────────────────────────┐│
│  │ Sidebar  │  Top bar: breadcrumbs · search · status · actions ││
│  │          ├──────────────────────────────────────────────────┤│
│  │ Modules  │  WORKSPACE (route outlet)                         ││
│  │ Watchlist│  ┌─────────────────────────────────────────────┐ ││
│  │ Recent   │  │ Module-specific layout (dashboard / pair…)   │ ││
│  │          │  └─────────────────────────────────────────────┘ ││
│  │          ├──────────────────────────────────────────────────┤│
│  │          │  Status bar: data stamp · API health · scan state  ││
│  └──────────┴──────────────────────────────────────────────────┘│
│  Command palette (portal, global) · Toasts · Dialogs              │
└─────────────────────────────────────────────────────────────────┘
```

**Not** “19 pages.” **One app** with **modules** mapped to existing Next.js routes (unchanged URLs for SEO/bookmarks).

---

## 2. Current vs target

| Aspect | Current (`web/app/layout.tsx`) | Target |
|--------|--------------------------------|--------|
| Chrome | Top header + `AppNav` | Sidebar + top bar + status bar |
| Width | `max-w-6xl` centered | Fluid workspace (padding only) |
| Search | None | Command palette + symbol jump |
| Context | None | Breadcrumbs, recent symbols |
| State | Per-page SWR | Shell providers + same SWR keys |

---

## 3. Directory architecture (proposed)

```
web/
├── app/                          # Next.js routes (keep paths)
│   ├── layout.tsx                # Root: fonts, providers, AppShell
│   └── (workspace)/              # Optional route group — same URLs
│       ├── page.tsx              # Dashboard module
│       ├── pair/[symbol]/page.tsx
│       └── …
├── components/
│   ├── ui/                       # shadcn primitives
│   ├── shell/                    # AppShell, Sidebar, TopBar, StatusBar
│   ├── command/                  # CommandPalette, shortcuts
│   ├── modules/                  # Dashboard, Pair, … composed views
│   └── legacy/                   # Temporary re-exports during migration
├── lib/
│   ├── api.ts                    # UNCHANGED contract
│   ├── navigation.ts             # Module registry, icons, paths
│   ├── command-registry.ts       # Palette actions
│   ├── keyboard.ts               # Shortcut bindings
│   └── workspace-prefs.ts        # localStorage layouts
├── hooks/
│   ├── use-recent-symbols.ts
│   └── use-pinned-symbols.ts
└── styles/
    └── tokens.css                # CSS variables
```

Migration strategy: wrap existing components in `modules/*` first; replace innards incrementally.

---

## 4. Application shell

### 4.1 Sidebar (persistent)

**Sections:**

1. **Quick** — Command (⌘K hint), Dashboard  
2. **Markets** — Heatmap, Compare, Correlation  
3. **Research** — Context (news), Macro, Flows, Engine  
4. **Workspace** — Portfolio, History, Notebook, Alerts  
5. **System** — Backtests, Status, Integrations, Glossary  

**Footer block:**

- Pinned symbols (from `localStorage`, max 8)
- Recent symbols (LRU, max 5)
- Collapse control

**Behavior:** Collapsible to icon rail; state in `localStorage`. Active route highlights module.

### 4.2 Top bar

| Zone | Content |
|------|---------|
| Left | Breadcrumbs (`Markets › BTC/USDT`) |
| Center | Optional module title (mobile) |
| Right | Global search trigger · Scan status pill · “Data as of …” · Settings link |

### 4.3 Status bar (bottom, optional desktop)

- Engine health dot (poll `/health` summary)
- Last scan UTC
- Calibration freshness (from calibrate status if cached client-side)
- Disclaimer one-liner (truncated)

### 4.4 Notifications

- **Sonner toasts:** scan complete, save integration, calibrate started/finished, API errors
- No push notifications in v1 (no backend change)

---

## 5. Navigation architecture

### Module registry (`lib/navigation.ts`)

Each entry:

```ts
{
  id: "dashboard",
  label: "Dashboard",
  href: "/",
  icon: LayoutDashboard,
  section: "quick",
  shortcut?: "g d",
}
```

All 19 routes registered; pair route pattern `/pair/[symbol]` dynamic.

### Breadcrumbs

- Static segments from registry
- Dynamic: symbol decoded from URL
- Clicking “Markets” → heatmap or dashboard (configurable)

### Workspace switcher (phase 2)

Dropdown: Trading | Research | Portfolio | Compact | News  
Changes **default landing module** + sidebar emphasis + density token — not separate apps.

---

## 6. Command palette

**Implementation:** shadcn `Command` + `cmdk` in `components/command/CommandPalette.tsx`.

**Global provider:** `CommandProvider` in root layout; listens `⌘K`, `/`.

### Command groups

| Group | Actions |
|-------|---------|
| **Symbols** | Analyze BTC/USDT, ETH/USDT, … (typeahead; recent + pinned first) |
| **Navigation** | Go to Dashboard, Portfolio, History, … |
| **Actions** | Refresh scan (navigate to `/` + mutate SWR key), Open compare with A/B |
| **Recent** | Last 5 pair routes |
| **Settings** | Integrations, Alerts |

**Symbol search:** Client-side filter on pinned + recent + top scan results (from last `scan` SWR cache if mounted). Deep link: `/pair/BTC%2FUSDT`.

**No new API** for search — optional enhancement later: prefix `>` for commands only.

### Palette UX

- Modal centered, max-w-xl, `elevation-2`
- Fuzzy filter on label + keywords
- Enter → navigate or execute
- Esc → close

---

## 7. Keyboard shortcut system

**Implementation:** `hooks/use-keyboard-shortcuts.ts` — attach at shell level; ignore when input focused.

| Shortcut | Action |
|----------|--------|
| `⌘K` / `Ctrl+K` | Open command palette |
| `/` | Open palette (search mode) |
| `G` then `D` | Dashboard |
| `G` then `P` | Portfolio |
| `G` then `H` | History |
| `G` then `E` | Engine docs |
| `G` then `S` | Status |
| `⌘B` / `Ctrl+B` | Toggle sidebar |
| `[` | Collapse sidebar (alt) |
| `?` | Shortcuts help dialog |

**Pair module (when route matches `/pair/*`):**

| Shortcut | Action |
|----------|--------|
| `1–7` | Switch tabs (Overview, Structure, …) |
| `⌘↵` | Refresh analyze (mutate SWR) |

Document in Glossary page + shortcuts dialog.

---

## 8. Module layouts

### 8.1 Dashboard module (`/`)

**Above the fold (no scroll on 900px height):**

```
┌─────────────────────────────────────────────────────────────┐
│ KPI: Actionable │ Regime (BTC) │ Scan │ Cal WF │ Port. heat │
├───────────────────────────────┬─────────────────────────────┤
│ Scan table (TanStack)         │ Rejection breakdown         │
│                               │ Mini heatmap                │
├───────────────────────────────┴─────────────────────────────┤
│ Watchlist row (horizontal chips)                             │
└─────────────────────────────────────────────────────────────┘
```

**Data:** `api.scan`, `api.portfolioAnalytics` (default equity), calibrate status from SWR cache or lightweight fetch.

### 8.2 Pair module (`/pair/[symbol]`)

**Hierarchy:**

```
┌─ HERO (sticky) ─────────────────────────────────────────────┐
│ SYMBOL · TF selector · ACTION (large) · Score · Regime pill │
│ Entry │ SL │ TP1 │ TP2 │ R:R  (mono row)                     │
└─────────────────────────────────────────────────────────────┘
┌─ CHART (fixed height) ──────────────────────────────────────┐
│ Lightweight Charts + level lines from verdict JSON           │
└─────────────────────────────────────────────────────────────┘
┌─ TABS ──────────────────────────────────────────────────────┐
│ Overview │ Lanes │ Structure │ Plan │ Replay │ Context │ …  │
└─────────────────────────────────────────────────────────────┘
```

**Tab → existing components (no logic change):**

| Tab | Components |
|-----|------------|
| Overview | TrustCard, SignalAttribution, Verdict reasons, ScoreGauge |
| Lanes | LanePanel |
| Structure | StructureEventsPanel, LiquiditySnapshotPanel, ChartOverlays list |
| Plan | TradePlanBox, LifecycleStepper (wire to API lifecycle when available) |
| Replay | ReplayTimeline |
| Context | NewsContextPanel, link to macro |
| History | ConfidenceHistoryChart (symbol scoped) |
| Coach | CopilotPanel + CoachPanel (accordion) |

**Right rail (xl+):** Collapsible “Explain” stack.

### 8.3 Other modules

Uniform **ModuleHeader** + content; tables use shared DataTable.

---

## 9. Client state architecture

| State | Storage | Notes |
|-------|---------|-------|
| Server data | SWR (unchanged keys) | `scan-1h`, `analyze`, etc. |
| Watchlist | localStorage | Existing key preserved |
| Pinned symbols | localStorage | New key `downpour.pinned` |
| Recent symbols | localStorage | Update on pair visit |
| Sidebar collapsed | localStorage | |
| Workspace preset | localStorage | |
| Command palette | React state | Ephemeral |

**No Redux.** Optional `zustand` only if shell state grows — prefer React context for shell.

---

## 10. Providers (root layout)

```tsx
<ThemeProvider>           // dark default
  <TooltipProvider>
    <CommandProvider>
      <AppShell>
        {children}
      </AppShell>
      <CommandPalette />
      <Toaster />
    </CommandProvider>
  </TooltipProvider>
</ThemeProvider>
```

---

## 11. Performance architecture

- **Lazy load** Lightweight Charts on pair route only (`dynamic(..., { ssr: false })`).
- **Lazy load** Recharts on history/backtests.
- Keep shell JS minimal; code-split per module.
- SWR `dedupingInterval` unchanged unless measured issues.
- Prefetch pair route on scan table row hover (`Link prefetch`).

---

## 12. Accessibility architecture

- Focus order: sidebar → main → status bar.
- Route change: focus main heading (`h1`) via `useEffect` (pair symbol).
- Command palette: Radix focus trap.
- Live region for scan complete toast (`aria-live="polite"`).

---

## 13. Migration phases (see roadmap)

1. Shell + tokens + shadcn (routes still old content)  
2. Dashboard module  
3. Pair module  
4. DataTable rollout  
5. Command palette + shortcuts  
6. Remaining modules skinned  

**URLs never change.** **api.ts never changes.**

---

## 14. Future (no backend required)

- Layout presets per workspace (CSS grid templates)
- Split pane pair + context (react-resizable-panels)
- Client-side Binance klines for chart (public API) — document ToS; optional

---

*Architecture owner: frontend team. Review when adding routes or API client methods.*
