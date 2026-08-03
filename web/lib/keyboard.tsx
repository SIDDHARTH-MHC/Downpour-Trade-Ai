"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useCommandPalette } from "@/components/command/CommandPaletteProvider";
import { useShortcutsDialog } from "@/components/command/ShortcutsProvider";
import { useSidebar } from "@/components/shell/SidebarProvider";
import { GOTO_ROUTES } from "@/lib/shortcuts";

export function useGlobalKeyboardShortcuts() {
  const router = useRouter();
  const { setOpen: setCommandOpen } = useCommandPalette();
  const { setOpen: setShortcutsOpen } = useShortcutsDialog();
  const { toggle: toggleSidebar } = useSidebar();

  useEffect(() => {
    let pendingG = false;
    let gTimer: ReturnType<typeof setTimeout> | null = null;

    function onKeyDown(e: KeyboardEvent) {
      const target = e.target as HTMLElement | null;
      const typing =
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.tagName === "SELECT" ||
          target.isContentEditable);

      if (typing) return;

      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "b") {
        e.preventDefault();
        toggleSidebar();
        return;
      }

      if (e.key === "?" && !e.metaKey && !e.ctrlKey) {
        e.preventDefault();
        setShortcutsOpen(true);
        return;
      }

      if (e.key === "/" && !e.metaKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        setCommandOpen(true);
        return;
      }

      if (e.key.toLowerCase() === "g" && !e.metaKey && !e.ctrlKey) {
        pendingG = true;
        if (gTimer) clearTimeout(gTimer);
        gTimer = setTimeout(() => {
          pendingG = false;
        }, 1200);
        return;
      }

      if (pendingG && !e.metaKey && !e.ctrlKey) {
        const href = GOTO_ROUTES[e.key.toLowerCase()];
        if (href) {
          e.preventDefault();
          pendingG = false;
          if (gTimer) clearTimeout(gTimer);
          router.push(href);
        }
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      if (gTimer) clearTimeout(gTimer);
    };
  }, [router, setCommandOpen, setShortcutsOpen, toggleSidebar]);
}

export function GlobalKeyboardShortcuts() {
  useGlobalKeyboardShortcuts();
  return null;
}
