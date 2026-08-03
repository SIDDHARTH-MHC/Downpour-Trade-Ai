"use client";

import useSWR from "swr";
import { api } from "@/lib/api";

function SentimentBadge({ sentiment }: { sentiment?: string }) {
  const s = sentiment || "Neutral";
  const cls =
    s === "Bullish" ? "text-long bg-long/10" : s === "Bearish" ? "text-short bg-short/10" : "text-muted bg-slate-800";
  return <span className={`rounded px-1.5 py-0.5 text-[10px] uppercase ${cls}`}>{s}</span>;
}

export function NewsContextPanel({ symbol }: { symbol: string }) {
  const { data, error, isLoading } = useSWR(["news", symbol], () => api.contextNews(symbol, 12), {
    refreshInterval: 900_000,
  });

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">News &amp; context</h3>
      <p className="text-xs text-muted">
        Aggregated RSS (CoinDesk, Cointelegraph, Fed, Binance, …) — never affects scores
      </p>
      {data?.feed_count != null && (
        <p className="mt-1 text-xs text-muted">{data.feed_count} sources · {data.aggregated_at_utc}</p>
      )}
      {isLoading && <p className="mt-2 text-sm text-muted">Loading headlines…</p>}
      {error && <p className="mt-2 text-sm text-red-400">{(error as Error).message}</p>}
      {data && (
        <ul className="mt-3 space-y-3 text-sm">
          {data.headlines.map((h, i) => (
            <li key={i} className="border-b border-border/30 pb-2">
              <div className="flex flex-wrap items-center gap-2">
                <SentimentBadge sentiment={h.sentiment} />
                {h.category && <span className="text-[10px] uppercase text-muted">{h.category}</span>}
                {h.symbols?.map((sym) => (
                  <span key={sym} className="rounded bg-slate-800 px-1 text-[10px]">
                    {sym}
                  </span>
                ))}
              </div>
              <div className="mt-1">
                {h.url ? (
                  <a href={h.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline">
                    {h.title}
                  </a>
                ) : (
                  <span>{h.title}</span>
                )}
              </div>
              {h.source && <span className="text-xs text-muted">{h.source}</span>}
            </li>
          ))}
          {data.headlines.length === 0 && <li className="text-muted">No headlines matched this symbol.</li>}
        </ul>
      )}
    </div>
  );
}
