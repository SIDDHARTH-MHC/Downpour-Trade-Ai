"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { VerdictCard } from "@/components/VerdictCard";
import { LanePanel } from "@/components/LanePanel";
import { ScoreGauge } from "@/components/ScoreGauge";
import { TradePlanBox } from "@/components/TradePlanBox";
import { TrustCard } from "@/components/TrustCard";
import { SignalAttribution } from "@/components/SignalAttribution";
import { StructureEventsPanel } from "@/components/StructureEventsPanel";
import { CopilotPanel } from "@/components/CopilotPanel";
import { ChartOverlaysPanel } from "@/components/ChartOverlaysPanel";
import { CoachPanel } from "@/components/CoachPanel";
import { NewsContextPanel } from "@/components/NewsContextPanel";
import { LiquiditySnapshotPanel } from "@/components/LiquiditySnapshotPanel";
import { LifecycleStepper, ReplayTimeline } from "@/components/ReplayLifecycle";
import { ConfidenceHistoryChart } from "@/components/ConfidenceHistoryChart";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function PairPage({ params }: { params: { symbol: string } }) {
  const symbol = decodeURIComponent(params.symbol);
  const [tf, setTf] = useState("1h");
  const { data, error, isLoading } = useSWR(["analyze", symbol, tf], () => api.analyze(symbol, tf), {
    refreshInterval: 60_000,
  });
  const { data: confHist } = useSWR(["conf-hist", symbol], () => api.confidenceHistory(symbol, 20), {
    refreshInterval: 120_000,
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
          <TrustCard trust={data.trust} />
          <VerdictCard verdict={data} />
          <SignalAttribution verdict={data} />
          <ScoreGauge score={data.weighted_score} />
          <StructureEventsPanel events={data.structure_events} />
          <CopilotPanel symbol={symbol} tf={tf} />
          <CoachPanel symbol={symbol} action={data.action} />
          <ChartOverlaysPanel verdict={data} />
          <NewsContextPanel symbol={symbol} />
          <LiquiditySnapshotPanel symbol={symbol} />
          {data.replay_events && data.replay_events.length > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold">Replay</h3>
              <p className="text-xs text-muted">Deterministic path to this verdict</p>
              <div className="mt-3">
                <ReplayTimeline events={data.replay_events} />
              </div>
            </div>
          )}
          {data.trade_plan && data.action !== "NO_TRADE" && (
            <LifecycleStepper
              lifecycle={{
                stage: data.trade_plan.patient ? "waiting" : "confirmed",
                label: data.trade_plan.patient ? "Waiting (patient entry)" : "Confirmed",
                steps: [
                  { id: "detected", label: "Detected", status: "done" },
                  {
                    id: "waiting",
                    label: "Waiting",
                    status: data.trade_plan.patient ? "current" : "done",
                  },
                  {
                    id: "confirmed",
                    label: "Confirmed",
                    status: data.trade_plan.patient ? "upcoming" : "current",
                  },
                ],
              }}
            />
          )}
          <LanePanel lanes={data.lanes} />
          {data.trade_plan && <TradePlanBox plan={data.trade_plan} />}
          {confHist && confHist.count > 0 && (
            <div className="card">
              <h3 className="text-sm font-semibold">Confidence history</h3>
              <p className="text-xs text-muted">Past signals for {symbol} with resolved outcomes</p>
              <div className="mt-3">
                <ConfidenceHistoryChart points={confHist.points} />
              </div>
            </div>
          )}
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
