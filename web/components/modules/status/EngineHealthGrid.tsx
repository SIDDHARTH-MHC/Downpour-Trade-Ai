import type { EngineStatusResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";

export function EngineHealthGrid({ data }: { data: EngineStatusResponse }) {
  const ok = data.status === "ok";

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className={cn("h-2.5 w-2.5 rounded-full", ok ? "bg-positive" : "bg-warning")} aria-hidden />
        <span className="text-sm text-muted-foreground">System</span>
        <Badge variant={ok ? "success" : "warning"}>{data.status}</Badge>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
        {Object.entries(data.checks).map(([name, check]) => {
          const checkOk = check.status === "ok";
          return (
            <Card
              key={name}
              className={cn(
                "relative overflow-hidden border-border/80",
                checkOk ? "border-l-2 border-l-positive" : "border-l-2 border-l-warning"
              )}
            >
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm font-medium capitalize tracking-tight">{name.replace(/_/g, " ")}</p>
                  <Badge variant={checkOk ? "success" : "warning"} className="shrink-0 text-[10px]">
                    {check.status}
                  </Badge>
                </div>
                <p className="mt-2 font-mono text-[11px] leading-relaxed text-muted-foreground">{check.detail}</p>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
