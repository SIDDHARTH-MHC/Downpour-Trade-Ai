"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useCommandPalette } from "@/components/command/CommandPaletteProvider";

const GOTO: Record<string, string> = {
  d: "/",
  p: "/portfolio",
  h: "/history",
  b: "/backtests",
  n: "/news",
};

export function useGlobalKeyboardShortcuts() {
  const router = useRouter();
  const { setOpen } = useCommandPalette();

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

      if (e.key === "/" && !e.metaKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        setOpen(true);
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
        const href = GOTO[e.key.toLowerCase()];
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
  }, [router, setOpen]);
}

export function GlobalKeyboardShortcuts() {
  useGlobalKeyboardShortcuts();
  return null;
}
