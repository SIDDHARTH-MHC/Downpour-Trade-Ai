"use client";

import type { ReactNode } from "react";
import type { Verdict } from "@/lib/api";
import type { ConfidenceHistoryResponse } from "@/lib/api";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent } from "@/components/ui/card";
import { binanceSymbol } from "@/lib/chart-levels";

type PairDetailTabsProps = {
  symbol: string;
  tf: string;
  verdict: Verdict;
  confHist?: ConfidenceHistoryResponse;
};

function Panel({ children }: { children: ReactNode }) {
  return <div className="space-y-4">{children}</div>;
}

export function PairDetailTabs({ symbol, tf, verdict, confHist }: PairDetailTabsProps) {
  const tvInterval = tf === "15m" ? "15" : tf === "4h" ? "240" : "60";

  return (
    <Tabs defaultValue="overview" className="w-full">
      <TabsList className="flex h-auto w-full flex-wrap justify-start gap-1">
        <TabsTrigger value="overview">Overview</TabsTrigger>
        <TabsTrigger value="lanes">Lanes</TabsTrigger>
        <TabsTrigger value="structure">Structure</TabsTrigger>
        <TabsTrigger value="plan">Plan</TabsTrigger>
        <TabsTrigger value="replay">Replay</TabsTrigger>
        <TabsTrigger value="context">Context</TabsTrigger>
        <TabsTrigger value="history">History</TabsTrigger>
        <TabsTrigger value="coach">Coach</TabsTrigger>
      </TabsList>

      <TabsContent value="overview">
        <Panel>
          <TrustCard trust={verdict.trust} />
          <SignalAttribution verdict={verdict} />
          <ScoreGauge score={verdict.weighted_score} />
          {verdict.reasons?.length ? (
            <Card>
              <CardContent className="p-4 text-sm text-muted-foreground">{verdict.reasons.join(" · ")}</CardContent>
            </Card>
          ) : null}
          <Card className="overflow-hidden">
            <CardContent className="p-0 pt-2">
              <p className="px-4 pb-2 text-xs text-muted-foreground">TradingView embed (reference)</p>
              <iframe
                title={`${symbol} TradingView`}
                className="h-[380px] w-full border-0"
                src={`https://s.tradingview.com/widgetembed/?symbol=BINANCE:${binanceSymbol(symbol)}&interval=${tvInterval}&theme=dark`}
              />
            </CardContent>
          </Card>
        </Panel>
      </TabsContent>

      <TabsContent value="lanes">
        <LanePanel lanes={verdict.lanes} />
      </TabsContent>

      <TabsContent value="structure">
        <Panel>
          <StructureEventsPanel events={verdict.structure_events} />
          <LiquiditySnapshotPanel symbol={symbol} />
          <ChartOverlaysPanel verdict={verdict} />
        </Panel>
      </TabsContent>

      <TabsContent value="plan">
        <Panel>
          {verdict.trade_plan ? <TradePlanBox plan={verdict.trade_plan} /> : (
            <Card>
              <CardContent className="p-4 text-sm text-muted-foreground">No active trade plan for this verdict.</CardContent>
            </Card>
          )}
          {verdict.trade_plan && verdict.action !== "NO_TRADE" && (
            <LifecycleStepper
              lifecycle={{
                stage: verdict.trade_plan.patient ? "waiting" : "confirmed",
                label: verdict.trade_plan.patient ? "Waiting (patient entry)" : "Confirmed",
                steps: [
                  { id: "detected", label: "Detected", status: "done" },
                  {
                    id: "waiting",
                    label: "Waiting",
                    status: verdict.trade_plan.patient ? "current" : "done",
                  },
                  {
                    id: "confirmed",
                    label: "Confirmed",
                    status: verdict.trade_plan.patient ? "upcoming" : "current",
                  },
                ],
              }}
            />
          )}
        </Panel>
      </TabsContent>

      <TabsContent value="replay">
        {verdict.replay_events && verdict.replay_events.length > 0 ? (
          <Card>
            <CardContent className="space-y-3 p-4">
              <div>
                <h3 className="text-sm font-semibold">Replay</h3>
                <p className="text-xs text-muted-foreground">Deterministic path to this verdict</p>
              </div>
              <ReplayTimeline events={verdict.replay_events} />
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-4 text-sm text-muted-foreground">No replay events for this analysis.</CardContent>
          </Card>
        )}
      </TabsContent>

      <TabsContent value="context">
        <Panel>
          <NewsContextPanel symbol={symbol} />
        </Panel>
      </TabsContent>

      <TabsContent value="history">
        {confHist && confHist.count > 0 ? (
          <Card>
            <CardContent className="space-y-3 p-4">
              <div>
                <h3 className="text-sm font-semibold">Confidence history</h3>
                <p className="text-xs text-muted-foreground">Past signals for {symbol} with resolved outcomes</p>
              </div>
              <ConfidenceHistoryChart points={confHist.points} />
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="p-4 text-sm text-muted-foreground">No confidence history yet for this symbol.</CardContent>
          </Card>
        )}
      </TabsContent>

      <TabsContent value="coach">
        <Panel>
          <CopilotPanel symbol={symbol} tf={tf} />
          <CoachPanel symbol={symbol} action={verdict.action} />
        </Panel>
      </TabsContent>
    </Tabs>
  );
}
