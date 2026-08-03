"use client";

import { useState } from "react";
import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function PortfolioPage() {
  const [equity, setEquity] = useState(10_000);
  const { data, error, isLoading } = useSWR(["portfolio", equity], () => api.portfolioAnalytics(equity), {
    refreshInterval: 120_000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Portfolio analytics</h1>
        <p className="text-sm text-muted">Risk heat from open tracked signals at assumed 1% risk per trade</p>
      </div>
      <label className="text-sm">
        Account equity (USD)
        <input
          type="number"
          className="ml-2 w-32 rounded border border-border bg-slate-900 px-2 py-1"
          value={equity}
          onChange={(e) => setEquity(Number(e.target.value))}
        />
      </label>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <>
          <dl className="card grid grid-cols-2 gap-4 text-sm sm:grid-cols-4">
            <div>
              <dt className="text-muted">Open trades</dt>
              <dd className="text-xl font-semibold">{data.open_trades}</dd>
            </div>
            <div>
              <dt className="text-muted">Long / Short</dt>
              <dd className="text-xl font-semibold">
                {data.long_count} / {data.short_count}
              </dd>
            </div>
            <div>
              <dt className="text-muted">Total risk $</dt>
              <dd className="text-xl font-semibold">${data.total_risk_usd.toFixed(0)}</dd>
            </div>
            <div>
              <dt className="text-muted">Heat</dt>
              <dd className="text-xl font-semibold">{data.portfolio_heat_pct.toFixed(2)}%</dd>
            </div>
          </dl>
          <div className="card overflow-x-auto text-sm">
            <table className="min-w-full">
              <thead className="text-left text-muted">
                <tr>
                  <th className="pb-2">Symbol</th>
                  <th className="pb-2">Side</th>
                  <th className="pb-2">Risk $</th>
                  <th className="pb-2">R:R</th>
                </tr>
              </thead>
              <tbody>
                {data.positions.map((p, i) => (
                  <tr key={i} className="border-t border-border/60">
                    <td className="py-2">{p.symbol}</td>
                    <td className="py-2">{p.action}</td>
                    <td className="py-2">${p.risk_usd}</td>
                    <td className="py-2">{p.reward_risk?.toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {data.positions.length === 0 && <p className="text-muted">No open signals with trade plans.</p>}
          </div>
          <p className="text-xs text-muted">{data.disclaimer}</p>
        </>
      )}
    </div>
  );
}
