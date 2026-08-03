"use client";

import type { Verdict } from "@/lib/api";
import { RegimeBadge } from "@/components/RegimeBadge";
import { VerdictChip } from "@/components/shared/VerdictChip";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type SignalHeroProps = {
  verdict: Verdict;
  tf: string;
  onTfChange: (tf: string) => void;
};

function PlanMetric({ label, value, tone }: { label: string; value: string; tone?: "long" | "short" | "default" }) {
  return (
    <div className="min-w-[4.5rem] rounded-md border border-border/60 bg-card/80 px-2 py-1.5">
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div
        className={cn(
          "font-mono text-sm tabular-nums",
          tone === "long" && "text-long",
          tone === "short" && "text-short"
        )}
      >
        {value}
      </div>
    </div>
  );
}

export function SignalHero({ verdict, tf, onTfChange }: SignalHeroProps) {
  const plan = verdict.trade_plan;
  const actionTone =
    verdict.action === "LONG" ? "border-long/40 bg-long/5" : verdict.action === "SHORT" ? "border-short/40 bg-short/5" : "";

  return (
    <section
      className={cn(
        "sticky top-0 z-20 -mx-4 border-b border-border bg-background/95 px-4 py-3 backdrop-blur supports-[backdrop-filter]:bg-background/80 lg:-mx-6 lg:px-6",
        actionTone
      )}
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 space-y-1">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-2xl font-semibold tracking-tight">{verdict.symbol}</h1>
            <VerdictChip action={verdict.action} className="text-sm" />
          </div>
          <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
            <RegimeBadge regime={verdict.regime.name} tradeable={verdict.regime.tradeable} />
            <Badge variant="secondary">{verdict.confidence}</Badge>
            <span className="font-mono tabular-nums">Score {verdict.weighted_score.toFixed(1)}</span>
          </div>
        </div>
        <div className="flex gap-1">
          {["15m", "1h", "4h"].map((option) => (
            <Button
              key={option}
              type="button"
              size="sm"
              variant={tf === option ? "default" : "outline"}
              onClick={() => onTfChange(option)}
            >
              {option}
            </Button>
          ))}
        </div>
      </div>

      {plan && verdict.action !== "NO_TRADE" ? (
        <div className="mt-3 flex flex-wrap gap-2">
          <PlanMetric label="Entry" value={plan.entry.toFixed(4)} />
          <PlanMetric label="Stop" value={plan.stop_loss.toFixed(4)} tone="short" />
          <PlanMetric label="TP1" value={plan.tp1.toFixed(4)} tone="long" />
          <PlanMetric label="TP2" value={plan.tp2.toFixed(4)} tone="long" />
          <PlanMetric label="R:R" value={plan.reward_risk.toFixed(2)} />
          {plan.patient ? (
            <Badge variant="warning" className="self-center">
              Patient entry
            </Badge>
          ) : null}
        </div>
      ) : (
        <p className="mt-2 text-sm text-muted-foreground">
          {verdict.reasons?.length ? verdict.reasons.join(" · ") : "No trade plan — conditions not met."}
        </p>
      )}
    </section>
  );
}
