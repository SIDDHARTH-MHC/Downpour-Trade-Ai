"use client";

import { createContext, useContext, useMemo, useState, type ReactNode } from "react";

type ShortcutsContextValue = {
  open: boolean;
  setOpen: (open: boolean) => void;
};

const ShortcutsContext = createContext<ShortcutsContextValue | null>(null);

export function ShortcutsProvider({ children }: { children: ReactNode }) {
  const [open, setOpen] = useState(false);
  const value = useMemo(() => ({ open, setOpen }), [open]);
  return <ShortcutsContext.Provider value={value}>{children}</ShortcutsContext.Provider>;
}

export function useShortcutsDialog() {
  const ctx = useContext(ShortcutsContext);
  if (!ctx) throw new Error("useShortcutsDialog must be used within ShortcutsProvider");
  return ctx;
}
