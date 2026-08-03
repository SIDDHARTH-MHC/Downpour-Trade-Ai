"use client";

import Link from "next/link";
import type { CorrelationMatrixResponse } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

function corrCellStyle(value: number | null) {
  if (value == null || Number.isNaN(value)) return "bg-muted/30 text-muted-foreground";
  const v = Math.max(-1, Math.min(1, value));
  if (v >= 0.7) return "bg-long/25 text-long";
  if (v >= 0.3) return "bg-long/10 text-foreground";
  if (v <= -0.7) return "bg-short/25 text-short";
  if (v <= -0.3) return "bg-short/10 text-foreground";
  return "bg-muted/40 text-muted-foreground";
}

export function CorrelationHeatmap({ data }: { data: CorrelationMatrixResponse }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-base">Correlation vs {data.benchmark}</CardTitle>
        <CardDescription>
          {data.timeframe} · context only — not a trading signal
        </CardDescription>
      </CardHeader>
      <CardContent className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="text-left text-muted-foreground">
              <th className="pb-2 pr-3 font-medium">Pair</th>
              <th className="pb-2 pr-3 font-medium">Correlation</th>
              <th className="pb-2 font-medium">Beta vs BTC</th>
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row) => (
              <tr key={row.symbol} className="border-t border-border/60">
                <td className="py-2 pr-3">
                  <Link href={`/pair/${encodeURIComponent(row.symbol)}`} className="text-primary hover:underline">
                    {row.symbol}
                  </Link>
                </td>
                <td className="py-2 pr-3">
                  <div className="flex items-center gap-2">
                    <div
                      className={cn(
                        "min-w-[3.5rem] rounded px-2 py-1 text-center font-mono text-xs tabular-nums",
                        corrCellStyle(row.correlation)
                      )}
                    >
                      {row.correlation != null ? row.correlation.toFixed(3) : "—"}
                    </div>
                    <div className="hidden h-2 flex-1 max-w-[8rem] overflow-hidden rounded-full bg-muted sm:block">
                      {row.correlation != null ? (
                        <div
                          className={cn("h-full", row.correlation >= 0 ? "bg-long/60" : "bg-short/60")}
                          style={{ width: `${Math.abs(row.correlation) * 100}%`, marginLeft: row.correlation < 0 ? `${(1 - Math.abs(row.correlation)) * 100}%` : 0 }}
                        />
                      ) : null}
                    </div>
                  </div>
                </td>
                <td className="py-2 font-mono tabular-nums">
                  {row.beta_vs_btc != null ? row.beta_vs_btc.toFixed(3) : row.error ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
