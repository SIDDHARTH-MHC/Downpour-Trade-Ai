import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

type MetricTileProps = {
  label: string;
  value: ReactNode;
  hint?: string;
  status?: "ok" | "warn" | "neutral" | "scan";
  className?: string;
};

const statusDot: Record<NonNullable<MetricTileProps["status"]>, string> = {
  ok: "bg-positive",
  warn: "bg-warning",
  neutral: "bg-muted-foreground",
  scan: "bg-primary animate-pulse",
};

export function MetricTile({ label, value, hint, status, className }: MetricTileProps) {
  return (
    <div className={cn("rounded-lg border border-border bg-card px-3 py-2.5", className)}>
      <div className="flex items-center gap-1.5 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
        {status ? <span className={cn("h-1.5 w-1.5 rounded-full", statusDot[status])} aria-hidden /> : null}
        {label}
      </div>
      <div className="mt-0.5 font-mono text-xl font-semibold tabular-nums tracking-tight text-foreground">{value}</div>
      {hint ? <p className="mt-0.5 truncate text-[11px] text-muted-foreground">{hint}</p> : null}
    </div>
  );
}
