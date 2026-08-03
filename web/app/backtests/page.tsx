"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

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
      alert((err as Error).message);
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
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Calibration / backtest stats</h1>
          <p className="text-sm text-muted">Confidence labels are backed by measured historical win rates</p>
        </div>
        <button
          onClick={handleRunCalibrate}
          disabled={starting || data?.running}
          className="rounded bg-sky-600 px-4 py-2 text-sm font-medium disabled:opacity-50"
        >
          {data?.running ? "Calibrating…" : starting ? "Starting…" : "Run calibration"}
        </button>
      </div>
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
        <dl className="card grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
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
        </dl>
      )}

      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="card overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="pb-2">Bucket</th>
                <th className="pb-2">Trades</th>
                <th className="pb-2">Win rate</th>
                <th className="pb-2">Avg R</th>
                <th className="pb-2">Profit factor</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(buckets).map(([bucket, stats]) => (
                <tr key={bucket} className="border-t border-border/60">
                  <td className="py-2">{bucket}</td>
                  <td className="py-2">{stats.trade_count}</td>
                  <td className="py-2">{(stats.win_rate * 100).toFixed(1)}%</td>
                  <td className="py-2">{stats.avg_r.toFixed(2)}</td>
                  <td className="py-2">{Number(stats.profit_factor).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {Object.keys(buckets).length === 0 && !data.running && (
            <p className="text-sm text-muted">
              No calibration data yet. Click &quot;Run calibration&quot; to backtest BTC/USDT and ETH/USDT over 6
              months.
            </p>
          )}
        </div>
      )}
    </div>
  );
}
