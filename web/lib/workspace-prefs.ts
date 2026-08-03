import type { NavSection } from "@/lib/navigation";

export type WorkspaceId = "trading" | "research" | "portfolio" | "compact" | "news";
export type Density = "comfortable" | "compact";
export type ThemeMode = "dark" | "light" | "system";

export type WorkspacePreset = {
  id: WorkspaceId;
  label: string;
  description: string;
  defaultHref: string;
  emphasizeSections: NavSection[];
  density: Density;
};

export const WORKSPACE_PRESETS: WorkspacePreset[] = [
  {
    id: "trading",
    label: "Trading",
    description: "Scan, heatmap, portfolio risk",
    defaultHref: "/",
    emphasizeSections: ["quick", "markets", "workspace"],
    density: "comfortable",
  },
  {
    id: "research",
    label: "Research",
    description: "Context, macro, engine docs",
    defaultHref: "/news",
    emphasizeSections: ["research", "markets"],
    density: "comfortable",
  },
  {
    id: "portfolio",
    label: "Portfolio",
    description: "Exposure, history, alerts",
    defaultHref: "/portfolio",
    emphasizeSections: ["workspace", "markets"],
    density: "comfortable",
  },
  {
    id: "compact",
    label: "Compact",
    description: "Dense tables, minimal chrome",
    defaultHref: "/",
    emphasizeSections: ["quick", "markets"],
    density: "compact",
  },
  {
    id: "news",
    label: "News",
    description: "Context feed first",
    defaultHref: "/news",
    emphasizeSections: ["research"],
    density: "comfortable",
  },
];

const STORAGE = {
  workspace: "downpour.workspace",
  density: "downpour.density",
  theme: "downpour.theme",
} as const;

export function getWorkspacePreset(id: WorkspaceId): WorkspacePreset {
  return WORKSPACE_PRESETS.find((w) => w.id === id) ?? WORKSPACE_PRESETS[0];
}

export function readStoredWorkspace(): WorkspaceId {
  try {
    const raw = localStorage.getItem(STORAGE.workspace) as WorkspaceId | null;
    if (raw && WORKSPACE_PRESETS.some((w) => w.id === raw)) return raw;
  } catch {
    /* ignore */
  }
  return "trading";
}

export function readStoredDensity(): Density {
  try {
    const raw = localStorage.getItem(STORAGE.density);
    if (raw === "compact" || raw === "comfortable") return raw;
  } catch {
    /* ignore */
  }
  return "comfortable";
}

export function readStoredTheme(): ThemeMode {
  try {
    const raw = localStorage.getItem(STORAGE.theme);
    if (raw === "dark" || raw === "light" || raw === "system") return raw;
  } catch {
    /* ignore */
  }
  return "dark";
}

export function writeStoredWorkspace(id: WorkspaceId) {
  localStorage.setItem(STORAGE.workspace, id);
}

export function writeStoredDensity(density: Density) {
  localStorage.setItem(STORAGE.density, density);
}

export function writeStoredTheme(theme: ThemeMode) {
  localStorage.setItem(STORAGE.theme, theme);
}

export function resolveThemeClass(theme: ThemeMode): "dark" | "light" {
  if (theme === "light") return "light";
  if (theme === "dark") return "dark";
  if (typeof window !== "undefined" && window.matchMedia("(prefers-color-scheme: light)").matches) {
    return "light";
  }
  return "dark";
}

export function isSectionEmphasized(section: NavSection, workspace: WorkspaceId) {
  return getWorkspacePreset(workspace).emphasizeSections.includes(section);
}
