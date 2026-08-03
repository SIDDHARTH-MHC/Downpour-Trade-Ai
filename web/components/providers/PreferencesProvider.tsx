"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { useRouter } from "next/navigation";
import {
  type Density,
  type ThemeMode,
  type WorkspaceId,
  getWorkspacePreset,
  readStoredDensity,
  readStoredTheme,
  readStoredWorkspace,
  resolveThemeClass,
  writeStoredDensity,
  writeStoredTheme,
  writeStoredWorkspace,
} from "@/lib/workspace-prefs";

type PreferencesContextValue = {
  workspace: WorkspaceId;
  density: Density;
  theme: ThemeMode;
  setWorkspace: (id: WorkspaceId, options?: { navigate?: boolean }) => void;
  setDensity: (density: Density) => void;
  setTheme: (theme: ThemeMode) => void;
  hydrated: boolean;
};

const PreferencesContext = createContext<PreferencesContextValue | null>(null);

function applyDocumentPrefs(theme: ThemeMode, density: Density, workspace: WorkspaceId) {
  const root = document.documentElement;
  const resolved = resolveThemeClass(theme);
  root.classList.remove("dark", "light");
  root.classList.add(resolved);
  root.dataset.density = density;
  root.dataset.workspace = workspace;
}

export function PreferencesProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [workspace, setWorkspaceState] = useState<WorkspaceId>("trading");
  const [density, setDensityState] = useState<Density>("comfortable");
  const [theme, setThemeState] = useState<ThemeMode>("dark");
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    const ws = readStoredWorkspace();
    const den = readStoredDensity();
    const th = readStoredTheme();
    setWorkspaceState(ws);
    setDensityState(den);
    setThemeState(th);
    applyDocumentPrefs(th, den, ws);
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated || theme !== "system") return;
    const mq = window.matchMedia("(prefers-color-scheme: light)");
    const onChange = () => applyDocumentPrefs("system", density, workspace);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, [hydrated, theme, density, workspace]);

  const setWorkspace = useCallback(
    (id: WorkspaceId, options?: { navigate?: boolean }) => {
      const preset = getWorkspacePreset(id);
      setWorkspaceState(id);
      writeStoredWorkspace(id);
      setDensityState(preset.density);
      writeStoredDensity(preset.density);
      applyDocumentPrefs(theme, preset.density, id);
      if (options?.navigate !== false) {
        router.push(preset.defaultHref);
      }
    },
    [router, theme]
  );

  const setDensity = useCallback(
    (value: Density) => {
      setDensityState(value);
      writeStoredDensity(value);
      applyDocumentPrefs(theme, value, workspace);
    },
    [theme, workspace]
  );

  const setTheme = useCallback(
    (value: ThemeMode) => {
      setThemeState(value);
      writeStoredTheme(value);
      applyDocumentPrefs(value, density, workspace);
    },
    [density, workspace]
  );

  const value = useMemo(
    () => ({ workspace, density, theme, setWorkspace, setDensity, setTheme, hydrated }),
    [workspace, density, theme, setWorkspace, setDensity, setTheme, hydrated]
  );

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

export function usePreferences() {
  const ctx = useContext(PreferencesContext);
  if (!ctx) throw new Error("usePreferences must be used within PreferencesProvider");
  return ctx;
}
