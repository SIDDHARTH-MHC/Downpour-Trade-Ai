"use client";

import useSWR from "swr";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

export default function MacroPage() {
  const { data, error, isLoading } = useSWR("macro", () => api.macroSnapshot(), { refreshInterval: 300_000 });
  const { data: etf } = useSWR("etf", () => api.contextEtf(), { refreshInterval: 600_000 });

  const m = data?.macro;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Macro snapshot</h1>
        <p className="text-sm text-muted">Global crypto context (CoinGecko) — informs regime; not mixed into lane scores</p>
      </div>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {m?.error && <ErrorState message={m.error} />}
      {m && !m.error && (
        <dl className="card grid grid-cols-2 gap-4 text-sm sm:grid-cols-3">
          <div>
            <dt className="text-muted">BTC dominance</dt>
            <dd className="text-xl font-semibold">{m.btc_dominance?.toFixed(2)}%</dd>
          </div>
          <div>
            <dt className="text-muted">ETH dominance</dt>
            <dd className="text-xl font-semibold">{m.eth_dominance?.toFixed(2)}%</dd>
          </div>
          <div>
            <dt className="text-muted">Total market cap</dt>
            <dd className="text-xl font-semibold">${((m.total_market_cap_usd ?? 0) / 1e12).toFixed(2)}T</dd>
          </div>
          <div>
            <dt className="text-muted">24h mcap change</dt>
            <dd className="text-xl font-semibold">{m.market_cap_change_24h_pct?.toFixed(2)}%</dd>
          </div>
          <div>
            <dt className="text-muted">24h volume</dt>
            <dd className="text-xl font-semibold">${((m.total_volume_usd ?? 0) / 1e9).toFixed(1)}B</dd>
          </div>
        </dl>
      )}
      {etf?.etf && (
        <div className="card text-sm">
          <h2 className="font-semibold text-sky-300">ETF context</h2>
          <p className="mt-2 text-muted">{etf.etf.message}</p>
          <p className="mt-2">Reference: {etf.etf.reference_tickers.join(", ")}</p>
          <p className="mt-2 text-xs text-muted">{etf.etf.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
