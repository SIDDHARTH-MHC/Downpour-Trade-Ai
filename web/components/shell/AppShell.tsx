"use client";

import { useState, type ReactNode } from "react";
import { Sheet, SheetContent, SheetTitle } from "@/components/ui/sheet";
import { SidebarNav, SidebarNavMobile } from "@/components/shell/SidebarNav";
import { TopBar } from "@/components/shell/TopBar";
import { StatusBar } from "@/components/shell/StatusBar";
import { MobileNav } from "@/components/shell/MobileNav";
import { CommandPalette } from "@/components/command/CommandPalette";
import { ShortcutsDialog } from "@/components/command/ShortcutsDialog";
import { MainContentFocus } from "@/components/shell/MainContentFocus";
import { DisclaimerFooter } from "@/components/DisclaimerFooter";

export function AppShell({ children }: { children: ReactNode }) {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <div className="flex min-h-screen w-full">
        <SidebarNav />
        <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
          <SheetContent side="left" className="w-[min(100vw,18rem)] p-0 lg:hidden">
            <SheetTitle className="sr-only">Navigation</SheetTitle>
            <SidebarNavMobile onNavigate={() => setMobileOpen(false)} />
          </SheetContent>
        </Sheet>
        <div className="flex min-h-screen min-w-0 flex-1 flex-col">
          <MainContentFocus />
          <TopBar onOpenMobileNav={() => setMobileOpen(true)} />
          <main className="shell-main flex-1 overflow-x-hidden pb-24 lg:pb-6">
            <div className="mx-auto w-full max-w-[1600px]">{children}</div>
            <div className="mx-auto mt-10 max-w-[1600px]">
              <DisclaimerFooter />
            </div>
          </main>
          <StatusBar />
        </div>
      </div>
      <MobileNav />
      <CommandPalette />
      <ShortcutsDialog />
    </>
  );
}
