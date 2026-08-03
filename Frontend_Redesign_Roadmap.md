# Downpour Trade AI — Frontend Redesign Roadmap

**Version:** 1.0  
**Date:** 2026-08-04  
**Scope:** Frontend only. Preserve 100% functionality via existing `web/lib/api.ts`.

**Companion docs:** [Product_Design_System.md](./Product_Design_System.md) · [Application_Architecture.md](./Application_Architecture.md) · [Component_Inventory.md](./Component_Inventory.md) · [UI_UX_Audit.md](./UI_UX_Audit.md)

---

## 1. Scores

| Milestone | UI score target |
|-----------|-----------------|
| Today | **4.2 / 10** |
| After Phase C (shell + dashboard + pair) | **7.0 / 10** |
| After Phase F (full rollout + a11y) | **8.5 / 10** |

---

## 2. Design principles (execution)

1. **Shell first** — Users feel one app before pixel-polishing secondary modules.  
2. **Pair + Dashboard second** — Highest traffic and trust surface.  
3. **Tables third** — Professional trader expectation.  
4. **Command palette fourth** — Keyboard identity.  
5. **No backend tickets** — If data missing for KPI, derive from existing endpoints only or defer widget.

---

## 3. Priority implementation roadmap

### Phase A — Foundation (Week 1–2)

**Goal:** Tokens, shadcn, app shell wrapping existing page content.

| Task | Deliverable |
|------|-------------|
| A1 | Init shadcn, Geist fonts, `tokens.css`, update `tailwind.config` |
| A2 | `AppShell`, `SidebarNav`, `TopBar`, `MobileNav` |
| A3 | `ModuleHeader`, replace page h1 patterns (visual only) |
| A4 | Button/Input/Card migration on 2 pilot pages (Status, Glossary) |
| A5 | Sonner toasts; remove `alert()` from backtests |
| A6 | Lucide on sidebar |

**Exit criteria:** All routes reachable via sidebar; content still legacy components inside shell.

**Effort:** 5–8 dev-days · 2 design-days

---

### Phase B — Dashboard workstation (Week 2–3)

**Goal:** Answer market questions without scrolling.

| Task | Deliverable |
|------|-------------|
| B1 | `KPIRow`: actionable count, scan status, last scan (from `scan`) |
| B2 | `KPIRow`: portfolio heat (from `portfolioAnalytics` default equity) |
| B3 | `KPIRow`: calibration WF badge (from `calibrateStatus` cache) |
| B4 | `ScanTable` TanStack — sort/filter |
| B5 | `ScanRejectionChart` from `scan_report` |
| B6 | Full-width heatmap strip |

**Exit criteria:** 1080p viewport shows KPI + table header without scroll.

**Effort:** 6–9 dev-days · 3 design-days

---

### Phase C — Pair module (Week 3–5)

**Goal:** Hero hierarchy + chart + tabs; no card stack.

| Task | Deliverable |
|------|-------------|
| C1 | `SignalHero` sticky (replaces top VerdictCard layout) |
| C2 | `TradePlanPanel` mono row in hero |
| C3 | `PriceChart` (Lightweight Charts) + levels from verdict JSON |
| C4 | `PairTabs`: Overview, Lanes, Structure, Plan, Replay, Context, History, Coach |
| C5 | Mount existing panels inside tabs (zero API change) |
| C6 | Recent symbols hook on visit |

**Exit criteria:** Feature parity checklist vs current pair page (all panels reachable).

**Effort:** 10–14 dev-days · 4 design-days

---

### Phase D — Data tables & viz (Week 5–6)

| Task | Deliverable |
|------|-------------|
| D1 | History `DataTable` + filters |
| D2 | Flows, Portfolio, Backtests tables |
| D3 | `ConfidenceTimeline` Recharts polish |
| D4 | Correlation matrix visual |
| D5 | Compare side-by-side layout upgrade |
| D6 | Health grid Grafana-style |

**Effort:** 6–10 dev-days · 2 design-days

---

### Phase E — Command & keyboard (Week 6–7)

| Task | Deliverable |
|------|-------------|
| E1 | `CommandPalette` all modules + symbol jump |
| E2 | Shortcuts dialog |
| E3 | `G D`, `G P`, `G H`, `⌘B` |
| E4 | Pinned symbols in sidebar (extend watchlist storage) |

**Effort:** 4–6 dev-days · 1 design-day

---

### Phase F — Polish & a11y (Week 7–8)

| Task | Deliverable |
|------|-------------|
| F1 | Empty states all modules |
| F2 | Focus rings audit, skip link |
| F3 | `prefers-reduced-motion` |
| F4 | Mobile bottom nav + pair tab scroll |
| F5 | Remaining pages skinned (coach, notebook, alerts, …) |
| F6 | axe CI on dashboard + pair |

**Effort:** 4–6 dev-days · 2 design-days

---

### Phase G — Workspaces (optional, Week 9+)

| Task | Deliverable |
|------|-------------|
| G1 | Workspace switcher (localStorage) |
| G2 | Density token compact/comfortable |
| G3 | Light theme tokens |

**Effort:** 3–5 dev-days

---

## 4. Total effort estimate

| Role | Days |
|------|------|
| Frontend engineering | **35–52** |
| Product / UI design | **14–18** |
| QA (manual + a11y) | **5–8** |

**Calendar:** 8–10 weeks with 1 FTE engineer + part-time design.

---

## 5. Risk register

| Risk | Mitigation |
|------|------------|
| Chart without OHLCV API | v1 chart: last close + horizontal levels only; or client klines read-only |
| Bundle size | Dynamic import charts |
| Regression in data display | Tab parity checklist; no changes to `api.ts` |
| Scope creep | Defer workspaces, light theme, column resize to G |

---

## 6. GitHub repositories to study

| Repo | Learn |
|------|--------|
| [shadcn-ui/ui](https://github.com/shadcn-ui/ui) | Component patterns, theming |
| [shadcn-ui/taxonomy](https://github.com/shadcn-ui/taxonomy) | App layout |
| [tremorlabs/tremor](https://github.com/tremorlabs/tremor) | KPI rows |
| [calcom/cal.com](https://github.com/calcom/cal.com) | Shell, settings |
| [tradingview/lightweight-charts](https://github.com/tradingview/lightweight-charts) | Chart API |
| [TanStack/table](https://github.com/TanStack/table) | DataTable |
| [pacocoursey/cmdk](https://github.com/pacocoursey/cmdk) | Command palette |
| [openstatusHQ/openstatus](https://github.com/openstatusHQ/openstatus) | Status pages |
| [makeplane/plane](https://github.com/makeplane/plane) | Sidebar IA |
| [vercel/geist-font](https://github.com/vercel/geist-font) | Typography |

**UI kits (patterns only, do not install wholesale):** Origin UI, Magic UI, Syntax UI — study spacing, not aesthetics.

---

## 7. Product inspiration

| Product | Takeaway for Downpour |
|---------|----------------------|
| **TradingView** | Symbol header, watchlist, chart-centric pair |
| **CoinGlass** | Funding tables, heat colors, dark terminal |
| **Glassnode / CryptoQuant** | Metric cards, institutional tone |
| **Linear** | Sidebar, command menu, calm motion |
| **Raycast** | Palette UX, keyboard hints |
| **GitHub** | Tabs, breadcrumbs, density |
| **Vercel** | KPI cards, status pills, Geist |
| **Grafana / Datadog** | Engine health grids |
| **Stripe Dashboard** | Forms, empty states, trust |
| **Bloomberg Terminal** | Density discipline (not visual clone) |

---

## 8. Success metrics (UX)

| Metric | Target |
|--------|--------|
| Time to see actionable count on load | < 2s perceived (shell + KPI skeleton) |
| Clicks to any module | ≤ 2 (sidebar) or 1 (⌘K) |
| Pair: scroll to trust panel (old) | 0 scroll — trust in Overview tab hero vicinity |
| Lighthouse a11y (dashboard) | ≥ 90 |
| User-facing regressions | 0 missing panels vs pre-redesign |

---

## 9. Definition of done (program)

- [ ] All 19 routes function identically (same API calls, same fields shown)  
- [ ] Application shell on every route  
- [ ] Design system tokens — no raw `sky-600` on pages  
- [ ] Lucide only  
- [ ] Command palette navigates all modules  
- [ ] Dashboard KPI row shipped  
- [ ] Pair hero + tabs + chart shipped  
- [ ] Documentation updated (`web/README.md` — optional pointer to design system)  

---

## 10. What we explicitly will NOT do (this program)

- Change REST endpoints or payload shapes  
- Add auth / multi-tenant UI (unless already exists)  
- Remove features or panels  
- Crypto casino visuals  
- Full Bloomberg clone (density inspired, not layout copy)  

---

## 11. Immediate next step

**Start Phase A1:** `npx shadcn@latest init` in `web/`, add Geist, implement `AppShell` wrapping current `{children}` without rewriting module internals.

---

*Roadmap version bumps when phases slip or scope changes.*
