"use client";

import { useEffect, useRef, useState } from "react";
import {
  ColorType,
  createChart,
  LineSeries,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type UTCTimestamp,
} from "lightweight-charts";
import type { Verdict } from "@/lib/api";
import { binanceInterval, binanceSymbol, collectChartLevels, type ChartLevel } from "@/lib/chart-levels";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type PriceChartProps = {
  symbol: string;
  tf: string;
  verdict: Verdict;
  className?: string;
};

function levelColor(level: ChartLevel) {
  if (level.kind === "entry") return "hsl(199 89% 48%)";
  if (level.kind === "sl") return "hsl(0 84% 60%)";
  if (level.kind === "tp") return "hsl(142 71% 45%)";
  return "hsl(215 16% 57%)";
}

async function fetchBinanceCloses(symbol: string, interval: string): Promise<LineData<UTCTimestamp>[]> {
  const res = await fetch(
    `https://api.binance.com/api/v3/klines?symbol=${binanceSymbol(symbol)}&interval=${binanceInterval(interval)}&limit=180`
  );
  if (!res.ok) throw new Error("Could not load market candles");
  const rows = (await res.json()) as Array<[number, string, string, string, string, ...unknown[]]>;
  return rows.map(([t, , , , close]) => ({
    time: Math.floor(t / 1000) as UTCTimestamp,
    value: parseFloat(close),
  }));
}

export function PriceChart({ symbol, tf, verdict, className }: PriceChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const levels = collectChartLevels(verdict);
  const tvUrl = `https://www.tradingview.com/chart/?symbol=BINANCE:${binanceSymbol(symbol)}`;

  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;

    setLoading(true);
    setError(null);

    const chart = createChart(el, {
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "hsl(215 16% 57%)",
      },
      grid: {
        vertLines: { color: "hsl(220 20% 14%)" },
        horzLines: { color: "hsl(220 20% 14%)" },
      },
      rightPriceScale: { borderColor: "hsl(220 20% 20%)" },
      timeScale: { borderColor: "hsl(220 20% 20%)" },
      height: 360,
    });
    chartRef.current = chart;
    const series = chart.addSeries(LineSeries, { color: "hsl(199 89% 48%)", lineWidth: 2 });
    seriesRef.current = series;

    const ro = new ResizeObserver(() => {
      chart.applyOptions({ width: el.clientWidth });
    });
    ro.observe(el);
    chart.applyOptions({ width: el.clientWidth });

    let cancelled = false;
    fetchBinanceCloses(symbol, tf)
      .then((data) => {
        if (cancelled) return;
        series.setData(data);
        for (const lvl of levels) {
          series.createPriceLine({
            price: lvl.price,
            color: levelColor(lvl),
            lineWidth: 1,
            lineStyle: lvl.kind === "structure" ? 2 : 0,
            axisLabelVisible: true,
            title: lvl.label,
          });
        }
        chart.timeScale().fitContent();
      })
      .catch((e) => {
        if (!cancelled) setError((e as Error).message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- rebuild chart when symbol/tf/levels change
  }, [symbol, tf, verdict.timestamp, verdict.weighted_score]);

  return (
    <Card className={cn("overflow-hidden", className)}>
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="text-base">Price & levels</CardTitle>
          <CardDescription>Binance spot candles · engine levels overlaid</CardDescription>
        </div>
        <a href={tvUrl} target="_blank" rel="noreferrer" className="text-xs text-primary hover:underline">
          TradingView ↗
        </a>
      </CardHeader>
      <CardContent className="relative pb-2">
        {loading && !error ? (
          <div className="absolute inset-0 z-10 flex items-center justify-center bg-background/60 text-sm text-muted-foreground">
            Loading chart…
          </div>
        ) : null}
        {error ? (
          <p className="mb-2 text-sm text-destructive">{error}</p>
        ) : null}
        <div ref={containerRef} className="w-full min-h-[360px]" />
      </CardContent>
    </Card>
  );
}
