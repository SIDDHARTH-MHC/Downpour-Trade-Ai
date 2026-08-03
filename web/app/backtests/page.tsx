"use client";

import { useState } from "react";
import useSWR from "swr";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { CalibrationBucketsTable } from "@/components/modules/backtests/CalibrationBucketsTable";

export default function BacktestsPage() {
  const [starting, setStarting] = useState(false);
  const { data, error, isLoading, mutate } = useSWR("calibrate-status", () => api.calibrateStatus(), {
    refreshInterval: (latest) => (latest?.running ? 15_000 : 120_000),
  });

  async function handleRunCalibrate() {
    setStarting(true);
    try {
      await api.startCalibrate(6, "BTC/USDT,ETH/USDT", "1h");
      await mutate();
    } catch (err) {
      toast.error((err as Error).message);
    } finally {
      setStarting(false);
    }
  }

  const buckets = Object.fromEntries(
    Object.entries(data?.buckets || {}).filter(([, stats]) => typeof stats?.win_rate === "number")
  );

  const wf = data?.walk_forward || [];
  const wfPassed = wf.length > 0 && wf.every((w) => w.accepted);
  const totalTrades = Object.values(buckets).reduce((s, b) => s + (b.trade_count || 0), 0);
  const avgWr =
    totalTrades > 0
      ? Object.values(buckets).reduce((s, b) => s + b.win_rate * b.trade_count, 0) / totalTrades
      : null;

  return (
    <div className="space-y-4">
      <ModuleHeader
        title="Calibration / backtest stats"
        description="Confidence labels are backed by measured historical win rates"
        actions={
          <Button onClick={handleRunCalibrate} disabled={starting || data?.running}>
            {data?.running ? "Calibrating…" : starting ? "Starting…" : "Run calibration"}
          </Button>
        }
      />
      <DataStamp label={data?.data_as_of_utc} />

      {data?.running && (
        <p className="text-sm text-amber-400">
          Calibration in progress… {data.progress ? `(${data.progress})` : ""} This can take 10–30 minutes on
          Render.
        </p>
      )}
      {data?.last_error && <ErrorState message={data.last_error} />}
      {data?.last_calibrated_utc && data.last_calibrated_utc !== "never" && (
        <p className="text-sm text-muted">Last calibrated: {data.last_calibrated_utc}</p>
      )}

      {data && !data.running && Object.keys(buckets).length > 0 && (
        <Card>
          <CardContent className="grid grid-cols-2 gap-4 p-4 text-sm sm:grid-cols-4">
          <div>
            <dt className="text-muted">Pairs calibrated</dt>
            <dd className="text-lg font-semibold">{wf.length || "—"}</dd>
          </div>
          <div>
            <dt className="text-muted">OOS trades (buckets)</dt>
            <dd className="text-lg font-semibold">{totalTrades}</dd>
          </div>
          <div>
            <dt className="text-muted">Avg win rate</dt>
            <dd className="text-lg font-semibold">{avgWr != null ? `${(avgWr * 100).toFixed(1)}%` : "—"}</dd>
          </div>
          <div>
            <dt className="text-muted">Walk-forward</dt>
            <dd className="text-lg font-semibold">{wf.length ? (wfPassed ? "Passed" : "Failed") : "—"}</dd>
          </div>
          </CardContent>
        </Card>
      )}

      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && Object.keys(buckets).length === 0 && !data.running && (
        <p className="text-sm text-muted-foreground">
          No calibration data yet. Click &quot;Run calibration&quot; to backtest BTC/USDT and ETH/USDT over 6 months.
        </p>
      )}

      {data && (
        <CalibrationBucketsTable buckets={buckets} />
      )}
    </div>
  );
}
