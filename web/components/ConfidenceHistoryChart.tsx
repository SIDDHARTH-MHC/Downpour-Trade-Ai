"use client";

import { useMemo } from "react";
import Link from "next/link";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { ConfidencePoint } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

function OutcomeBadge({ outcome }: { outcome: string | null | undefined }) {
  if (!outcome) return <span className="text-muted-foreground">—</span>;
  const variant =
    outcome === "WIN" ? "success" : outcome === "LOSS" ? "destructive" : outcome === "OPEN" ? "warning" : "secondary";
  return <Badge variant={variant}>{outcome}</Badge>;
}

export function ConfidenceHistoryChart({ points }: { points: ConfidencePoint[] }) {
  const chartData = useMemo(() => {
    const counts: Record<string, number> = { WIN: 0, LOSS: 0, OPEN: 0, OTHER: 0 };
    for (const p of points) {
      const o = p.outcome || "OTHER";
      if (o in counts) counts[o] += 1;
      else counts.OTHER += 1;
    }
    return Object.entries(counts)
      .filter(([, n]) => n > 0)
      .map(([outcome, count]) => ({ outcome, count }));
  }, [points]);

  if (points.length === 0) {
    return <p className="text-sm text-muted-foreground">No LONG/SHORT history yet for this filter.</p>;
  }

  return (
    <div className="space-y-4">
      {chartData.length > 0 ? (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Outcome distribution</CardTitle>
            <CardDescription>Resolved and open signals in this window</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-40 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                  <XAxis dataKey="outcome" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{
                      background: "hsl(var(--popover))",
                      border: "1px solid hsl(var(--border))",
                      borderRadius: 8,
                      fontSize: 12,
                    }}
                  />
                  <Bar dataKey="count" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      ) : null}

      <div className="overflow-hidden rounded-xl border border-border">
        <div className="max-h-80 overflow-auto">
          <table className="min-w-full text-sm">
            <thead className="sticky top-0 bg-card text-left text-muted-foreground">
              <tr>
                <th className="px-3 py-2 font-medium">Time</th>
                <th className="px-3 py-2 font-medium">Pair</th>
                <th className="px-3 py-2 font-medium">Action</th>
                <th className="px-3 py-2 font-medium">Score</th>
                <th className="px-3 py-2 font-medium">Confidence</th>
                <th className="px-3 py-2 font-medium">Outcome</th>
              </tr>
            </thead>
            <tbody>
              {points.map((p, i) => (
                <tr key={i} className="border-t border-border/60 hover:bg-accent/30">
                  <td className="whitespace-nowrap px-3 py-2 text-xs text-muted-foreground">{p.timestamp}</td>
                  <td className="px-3 py-2">
                    <Link href={`/pair/${encodeURIComponent(p.symbol)}`} className="text-primary hover:underline">
                      {p.symbol}
                    </Link>
                  </td>
                  <td className={cn("px-3 py-2", p.action === "LONG" ? "text-long" : p.action === "SHORT" ? "text-short" : "")}>
                    {p.action}
                  </td>
                  <td className="px-3 py-2 font-mono tabular-nums">{p.weighted_score.toFixed(1)}</td>
                  <td className="max-w-[10rem] truncate px-3 py-2 text-muted-foreground">{p.confidence}</td>
                  <td className="px-3 py-2">
                    <OutcomeBadge outcome={p.outcome} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
