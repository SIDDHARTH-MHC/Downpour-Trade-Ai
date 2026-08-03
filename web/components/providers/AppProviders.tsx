"use client";

import { Toaster } from "sonner";
import { CommandPaletteProvider } from "@/components/command/CommandPaletteProvider";
import { ShortcutsProvider } from "@/components/command/ShortcutsProvider";
import { SidebarProvider } from "@/components/shell/SidebarProvider";
import { GlobalKeyboardShortcuts } from "@/lib/keyboard";

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <SidebarProvider>
      <CommandPaletteProvider>
        <ShortcutsProvider>
          <GlobalKeyboardShortcuts />
          {children}
          <Toaster theme="dark" position="bottom-right" richColors closeButton />
        </ShortcutsProvider>
      </CommandPaletteProvider>
    </SidebarProvider>
  );
}
