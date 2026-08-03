"use client";

import useSWR from "swr";
import { api } from "@/lib/api";

export function StatusBar() {
  const { data } = useSWR("engine-status-bar", () => api.engineStatus(), {
    refreshInterval: 120_000,
    revalidateOnFocus: false,
  });

  const ok = data?.status === "ok";

  return (
    <footer
      className="hidden h-[var(--statusbar-height)] shrink-0 items-center justify-between border-t border-border bg-card/50 px-4 text-[11px] text-muted-foreground lg:flex"
      aria-live="polite"
    >
      <span className="flex items-center gap-2">
        <span
          className={`h-1.5 w-1.5 rounded-full ${ok ? "bg-positive" : data ? "bg-warning" : "bg-muted-foreground"}`}
          aria-hidden
        />
        {data ? (ok ? "Engine healthy" : `Engine ${data.status}`) : "Checking engine…"}
        {data?.data_as_of_utc ? <span className="text-muted-foreground/80">· {data.data_as_of_utc}</span> : null}
      </span>
      <span className="truncate">
        Informational only — not financial advice. Deterministic signals, no LLM in the engine path.
      </span>
    </footer>
  );
}
