"use client";

import { useMemo } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { ScanReport } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const LABELS: Record<string, string> = {
  regime_block: "Regime / BTC gate",
  lane_conflict: "Lane conflict",
  structure_no_edge: "Structure no edge",
  weak_alignment: "Lanes not aligned",
  adverse_lane: "Adverse lane",
  score_neutral: "Score neutral",
  other: "Other",
};

type ScanRejectionChartProps = {
  report?: ScanReport | null;
};

export function ScanRejectionChart({ report }: ScanRejectionChartProps) {
  const data = useMemo(() => {
    if (!report?.rejection_reasons) return [];
    return Object.entries(report.rejection_reasons)
      .map(([key, count]) => ({
        key,
        label: LABELS[key] || key.replace(/_/g, " "),
        count,
      }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8);
  }, [report]);

  if (!report) {
    return (
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Rejection breakdown</CardTitle>
          <CardDescription>Available after the next full scan completes</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Rejection breakdown</CardTitle>
        <CardDescription>
          {report.rejected_count} NO_TRADE of {report.total_scanned} · {report.actionable_count} actionable
        </CardDescription>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <p className="text-sm text-muted-foreground">No rejection histogram yet.</p>
        ) : (
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical" margin={{ left: 4, right: 8, top: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" horizontal={false} />
                <XAxis type="number" tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 11 }} />
                <YAxis
                  type="category"
                  dataKey="label"
                  width={120}
                  tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
                />
                <Tooltip
                  contentStyle={{
                    background: "hsl(var(--popover))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  labelStyle={{ color: "hsl(var(--foreground))" }}
                />
                <Bar dataKey="count" fill="hsl(var(--primary))" radius={[0, 4, 4, 0]} maxBarSize={18} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
