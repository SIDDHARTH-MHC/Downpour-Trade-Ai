import Link from "next/link";
import type { Verdict } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

function scoreTone(score: number, action: Verdict["action"]) {
  if (action === "LONG") return "border-long/30 bg-long/10 text-long";
  if (action === "SHORT") return "border-short/30 bg-short/10 text-short";
  const abs = Math.abs(score);
  if (abs >= 25) return "border-border bg-muted/40 text-foreground";
  return "border-border bg-card text-muted-foreground";
}

type DashboardHeatmapStripProps = {
  results: Verdict[];
};

export function DashboardHeatmapStrip({ results }: DashboardHeatmapStripProps) {
  if (!results.length) return null;

  const sorted = [...results].sort((a, b) => Math.abs(b.weighted_score) - Math.abs(a.weighted_score));

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-medium">Market map</CardTitle>
        <Link href="/heatmap" className="text-xs text-primary hover:underline">
          Full heatmap
        </Link>
      </CardHeader>
      <CardContent className="pb-3">
        <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-thin">
          {sorted.map((row) => (
            <Link
              key={row.symbol}
              href={`/pair/${encodeURIComponent(row.symbol)}`}
              className={cn(
                "flex min-w-[4.5rem] shrink-0 flex-col items-center rounded-md border px-2 py-2 text-center transition-opacity hover:opacity-90",
                scoreTone(row.weighted_score, row.action)
              )}
            >
              <span className="text-[11px] font-semibold">{row.symbol.replace("/USDT", "")}</span>
              <span className="font-mono text-[10px] tabular-nums">{row.weighted_score.toFixed(0)}</span>
              <span className="text-[9px] uppercase opacity-80">{row.action === "NO_TRADE" ? "—" : row.action}</span>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
