"use client";

import { Toaster } from "sonner";
import { CommandPaletteProvider } from "@/components/command/CommandPaletteProvider";
import { ShortcutsProvider } from "@/components/command/ShortcutsProvider";
import { PreferencesProvider, usePreferences } from "@/components/providers/PreferencesProvider";
import { SidebarProvider } from "@/components/shell/SidebarProvider";
import { GlobalKeyboardShortcuts } from "@/lib/keyboard";
import { resolveThemeClass } from "@/lib/workspace-prefs";

function ThemedToaster() {
  const { theme, hydrated } = usePreferences();
  const resolved = hydrated && typeof window !== "undefined" ? resolveThemeClass(theme) : "dark";
  return <Toaster theme={resolved} position="bottom-right" richColors closeButton />;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <PreferencesProvider>
      <SidebarProvider>
        <CommandPaletteProvider>
          <ShortcutsProvider>
            <GlobalKeyboardShortcuts />
            {children}
            <ThemedToaster />
          </ShortcutsProvider>
        </CommandPaletteProvider>
      </SidebarProvider>
    </PreferencesProvider>
  );
}
