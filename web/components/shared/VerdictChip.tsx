import type { Verdict } from "@/lib/api";
import { cn } from "@/lib/utils";

export function VerdictChip({ action, className }: { action: Verdict["action"]; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-md px-2 py-0.5 text-xs font-semibold",
        action === "LONG" && "bg-long/20 text-long",
        action === "SHORT" && "bg-short/20 text-short",
        action === "NO_TRADE" && "bg-muted text-muted-foreground",
        className
      )}
    >
      {action}
    </span>
  );
}
