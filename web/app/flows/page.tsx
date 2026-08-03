"use client";

import { useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

const DEFAULT_SYMBOLS = "BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT";

export default function FlowsPage() {
  const [symbols, setSymbols] = useState(DEFAULT_SYMBOLS);
  const { data, error, isLoading, mutate } = useSWR(["flows", symbols], () => api.flowsSnapshot(symbols), {
    refreshInterval: 120_000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Funding &amp; flow snapshot</h1>
        <p className="text-sm text-muted">Live funding rate and OI change from Binance USD-M (same inputs as flow lane)</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <input
          className="min-w-[280px] flex-1 rounded border border-border bg-slate-900 px-3 py-2 text-sm"
          value={symbols}
          onChange={(e) => setSymbols(e.target.value)}
        />
        <button type="button" className="rounded bg-sky-700 px-4 py-2 text-sm" onClick={() => mutate()}>
          Refresh
        </button>
      </div>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="card overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="pb-2">Pair</th>
                <th className="pb-2">Funding %</th>
                <th className="pb-2">OI (USD)</th>
                <th className="pb-2">OI Δ 1 bar</th>
              </tr>
            </thead>
            <tbody>
              {data.rows.map((row) => (
                <tr key={row.symbol} className="border-t border-border/60">
                  <td className="py-2">
                    <Link href={`/pair/${encodeURIComponent(row.symbol)}`} className="text-sky-400 hover:underline">
                      {row.symbol}
                    </Link>
                  </td>
                  <td className="py-2">
                    {row.funding_rate_pct != null ? `${row.funding_rate_pct.toFixed(4)}%` : "—"}
                  </td>
                  <td className="py-2">
                    {row.open_interest_usd != null ? `$${(row.open_interest_usd / 1e6).toFixed(1)}M` : "—"}
                  </td>
                  <td className="py-2">
                    {row.oi_change_1bar != null ? `${(row.oi_change_1bar * 100).toFixed(2)}%` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
