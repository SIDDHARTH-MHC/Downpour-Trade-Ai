"use client";

import { Toaster } from "sonner";
import { CommandPaletteProvider } from "@/components/command/CommandPaletteProvider";
import { GlobalKeyboardShortcuts } from "@/lib/keyboard";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <CommandPaletteProvider>
      <GlobalKeyboardShortcuts />
      {children}
      <Toaster theme="dark" position="bottom-right" richColors closeButton />
    </CommandPaletteProvider>
  );
}
