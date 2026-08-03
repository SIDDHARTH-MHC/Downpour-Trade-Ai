"use client";

import useSWR from "swr";
import { api } from "@/lib/api";

export function NewsContextPanel({ symbol }: { symbol: string }) {
  const { data, error, isLoading } = useSWR(["news", symbol], () => api.contextNews(symbol), {
    refreshInterval: 900_000,
  });

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">News context</h3>
      <p className="text-xs text-muted">Does not affect engine scores</p>
      {isLoading && <p className="mt-2 text-sm text-muted">Loading headlines…</p>}
      {error && <p className="mt-2 text-sm text-red-400">{(error as Error).message}</p>}
      {data && (
        <ul className="mt-3 space-y-2 text-sm">
          {data.headlines.map((h, i) => (
            <li key={i}>
              {h.url ? (
                <a href={h.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline">
                  {h.title}
                </a>
              ) : (
                <span>{h.title}</span>
              )}
              {h.source && <span className="ml-2 text-xs text-muted">{h.source}</span>}
            </li>
          ))}
          {data.headlines.length === 0 && <li className="text-muted">No headlines matched this symbol.</li>}
        </ul>
      )}
    </div>
  );
}
