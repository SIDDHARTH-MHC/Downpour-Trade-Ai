"use client";

import Link from "next/link";
import type { CompareSide } from "@/lib/api";
import { VerdictChip } from "@/components/shared/VerdictChip";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

const LANES = ["technical", "flow", "structure"] as const;

function LaneBar({ label, score }: { label: string; score: number }) {
  const pct = Math.min(100, Math.abs(score));
  const positive = score >= 0;
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs capitalize text-muted-foreground">
        <span>{label}</span>
        <span className="font-mono tabular-nums text-foreground">{score.toFixed(0)}</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-muted">
        <div
          className={cn("h-full rounded-full", positive ? "bg-long/70" : "bg-short/70")}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

function CompareSideCard({ side }: { side: CompareSide }) {
  const action =
    side.action === "LONG" || side.action === "SHORT" || side.action === "NO_TRADE"
      ? side.action
      : "NO_TRADE";

  return (
    <Card className="h-full">
      <CardHeader className="pb-3">
        <Link href={`/pair/${encodeURIComponent(side.symbol)}`} className="text-lg font-semibold text-primary hover:underline">
          {side.symbol}
        </Link>
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <VerdictChip action={action} />
          <span className="font-mono text-sm tabular-nums">Score {side.weighted_score.toFixed(1)}</span>
        </div>
        <p className="text-xs text-muted-foreground">
          {side.regime} · {side.confidence}
        </p>
      </CardHeader>
      <CardContent className="space-y-3">
        {LANES.map((lane) => (
          <LaneBar key={lane} label={lane} score={side.lanes[lane] ?? 0} />
        ))}
      </CardContent>
    </Card>
  );
}

export function CompareColumns({ a, b }: { a: CompareSide; b: CompareSide }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <CompareSideCard side={a} />
      <CompareSideCard side={b} />
    </div>
  );
}
