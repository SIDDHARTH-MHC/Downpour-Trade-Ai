"use client";

import { useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

const DEFAULT = "BTC/USDT,ETH/USDT,SOL/USDT,XRP/USDT,DOGE/USDT,BNB/USDT";

export default function CorrelationPage() {
  const [symbols, setSymbols] = useState(DEFAULT);
  const { data, error, isLoading } = useSWR(["corr", symbols], () => api.correlationMatrix(symbols), {
    refreshInterval: 300_000,
  });

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Correlation explorer</h1>
        <p className="text-sm text-muted">Rolling correlation &amp; beta vs BTC (context only)</p>
      </div>
      <input
        className="w-full rounded border border-border bg-slate-900 px-3 py-2 text-sm"
        value={symbols}
        onChange={(e) => setSymbols(e.target.value)}
      />
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="card overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead className="text-left text-muted">
              <tr>
                <th className="pb-2">Pair</th>
                <th className="pb-2">Corr vs BTC</th>
                <th className="pb-2">Beta</th>
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
                  <td className="py-2">{row.correlation != null ? row.correlation.toFixed(3) : "—"}</td>
                  <td className="py-2">{row.beta_vs_btc != null ? row.beta_vs_btc.toFixed(3) : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
