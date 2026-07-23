"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { VerdictCard } from "@/components/VerdictCard";
import { LanePanel } from "@/components/LanePanel";
import { ScoreGauge } from "@/components/ScoreGauge";
import { TradePlanBox } from "@/components/TradePlanBox";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function PairPage({ params }: { params: { symbol: string } }) {
  const symbol = decodeURIComponent(params.symbol);
  const [tf, setTf] = useState("1h");
  const { data, error, isLoading } = useSWR(["analyze", symbol, tf], () => api.analyze(symbol, tf), {
    refreshInterval: 60_000,
  });

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">{symbol}</h1>
        <div className="flex gap-2">
          {["15m", "1h", "4h"].map((option) => (
            <button
              key={option}
              onClick={() => setTf(option)}
              className={`rounded px-3 py-1 text-sm ${tf === option ? "bg-sky-600" : "bg-slate-800"}`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
      <DataStamp label={data?.data_as_of_utc || data?.timestamp} />

      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <>
          <VerdictCard verdict={data} />
          <ScoreGauge score={data.weighted_score} />
          <LanePanel lanes={data.lanes} />
          {data.trade_plan && <TradePlanBox plan={data.trade_plan} />}
          <div className="card overflow-hidden">
            <div className="mb-2 text-sm text-muted">Chart</div>
            <iframe
              title={`${symbol} chart`}
              className="h-[420px] w-full rounded border border-border"
              src={`https://s.tradingview.com/widgetembed/?symbol=BINANCE:${symbol.replace("/", "")}&interval=${tf === "15m" ? "15" : tf === "4h" ? "240" : "60"}&theme=dark`}
            />
          </div>
        </>
      )}
    </div>
  );
}
