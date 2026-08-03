"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { ConfidenceHistoryChart } from "@/components/ConfidenceHistoryChart";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { EmptyState } from "@/components/shell/EmptyState";
import { HistoryTable } from "@/components/modules/history/HistoryTable";
import { Card, CardContent } from "@/components/ui/card";
import { History } from "lucide-react";

export default function HistoryPage() {
  const [actionFilter, setActionFilter] = useState<"all" | "LONG" | "SHORT" | "NO_TRADE">("all");
  const { data, error, isLoading } = useSWR("history", () => api.history(undefined, 50), {
    refreshInterval: 120_000,
  });
  const { data: confHist } = useSWR("conf-hist-all", () => api.confidenceHistory(undefined, 40), {
    refreshInterval: 120_000,
  });

  const wins = data?.verdicts.filter((v) => v.action !== "NO_TRADE").length ?? 0;

  return (
    <div className="space-y-4">
      <ModuleHeader title="Verdict history" description="Past signals with outcomes when resolved" />
      <DataStamp label={data?.data_as_of_utc} />

      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}

      {confHist && confHist.count > 0 && (
        <Card>
          <CardContent className="space-y-3 p-4">
            <div>
              <h2 className="text-lg font-semibold">Confidence history</h2>
              <p className="text-sm text-muted-foreground">LONG/SHORT signals with WIN / LOSS / OPEN</p>
            </div>
            <ConfidenceHistoryChart points={confHist.points} />
          </CardContent>
        </Card>
      )}

      {data && data.verdicts.length === 0 && (
        <EmptyState
          icon={History}
          title="No verdict history yet"
          description="Stored LONG/SHORT and NO_TRADE records will appear here after the API persists scans."
        />
      )}
      {data && data.verdicts.length > 0 && (
        <>
          <p className="text-sm text-muted-foreground">
            {data.count} records · {wins} non-NO-TRADE · {data.open_outcomes} open outcomes
          </p>
          <HistoryTable
            verdicts={data.verdicts}
            actionFilter={actionFilter}
            onActionFilterChange={setActionFilter}
          />
        </>
      )}
    </div>
  );
}
