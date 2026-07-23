"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function BacktestsPage() {
  const { data, error, isLoading } = useSWR("backtest-stats", () => api.backtestStats("BTC/USDT", "1h"), {
    refreshInterval: 300_000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Calibration / backtest stats</h1>
        <p className="text-sm text-muted">Confidence labels are backed by measured historical win rates</p>
      </div>
      <DataStamp label={data?.data_as_of_utc} />

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
              {Object.entries(data.buckets).map(([bucket, stats]) => (
                <tr key={bucket} className="border-t border-border/60">
                  <td className="py-2">{bucket}</td>
                  <td className="py-2">{stats.trade_count}</td>
                  <td className="py-2">{(stats.win_rate * 100).toFixed(1)}%</td>
                  <td className="py-2">{stats.avg_r.toFixed(2)}</td>
                  <td className="py-2">{stats.profit_factor.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {Object.keys(data.buckets).length === 0 && (
            <p className="text-sm text-muted">No calibration data yet. Run `python cli.py calibrate` on the API server.</p>
          )}
        </div>
      )}
    </div>
  );
}
