"use client";

import { useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

const TABS = [
  { id: "", label: "All (BTC focus)" },
  { id: "news", label: "News" },
  { id: "macro", label: "Macro" },
  { id: "exchange", label: "Exchange" },
] as const;

export default function NewsPage() {
  const [category, setCategory] = useState<(typeof TABS)[number]["id"]>("");
  const { data, error, isLoading } = useSWR(["news-page", category], () =>
    api.contextNews("BTC/USDT", 40, category || undefined)
  );

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Context feed</h1>
        <p className="text-sm text-muted">Owned RSS aggregator — deduped, symbol-tagged, heuristic sentiment</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {TABS.map((t) => (
          <button
            key={t.id || "all"}
            type="button"
            onClick={() => setCategory(t.id)}
            className={`rounded px-3 py-1 text-sm ${category === t.id ? "bg-sky-600" : "bg-slate-800"}`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <DataStamp label={data?.aggregated_at_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="card space-y-3 text-sm">
          {data.headlines.map((h, i) => (
            <article key={i} className="border-b border-border/40 pb-3">
              <div className="flex flex-wrap gap-2 text-xs">
                <span>{h.sentiment}</span>
                <span className="text-muted">{h.category}</span>
                {h.symbols?.map((s) => (
                  <Link key={s} href={`/pair/${encodeURIComponent(`${s}/USDT`)}`} className="text-sky-400">
                    {s}
                  </Link>
                ))}
              </div>
              <h2 className="mt-1 font-medium">
                {h.url ? (
                  <a href={h.url} target="_blank" rel="noreferrer" className="text-sky-400 hover:underline">
                    {h.title}
                  </a>
                ) : (
                  h.title
                )}
              </h2>
              <p className="text-muted">{h.source}</p>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
