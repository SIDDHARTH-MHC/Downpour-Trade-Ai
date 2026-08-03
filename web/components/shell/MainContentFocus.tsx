"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";

/** Move focus to the primary heading after client navigations (a11y). */
export function MainContentFocus() {
  const pathname = usePathname();

  useEffect(() => {
    const root = document.getElementById("main-content");
    const heading = root?.querySelector("h1");
    if (heading instanceof HTMLElement) {
      heading.setAttribute("tabindex", "-1");
      heading.focus({ preventScroll: true });
    }
  }, [pathname]);

  return null;
}
