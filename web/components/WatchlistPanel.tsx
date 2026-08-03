"use client";

import { useCallback, useEffect, useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { api, Verdict } from "@/lib/api";
import { PairTable } from "@/components/PairTable";
import { LoadingCard } from "@/components/DisclaimerFooter";

const STORAGE_KEY = "downpour_watchlist";

export function useWatchlist() {
  const [symbols, setSymbols] = useState<string[]>([]);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) setSymbols(JSON.parse(raw) as string[]);
    } catch {
      setSymbols([]);
    }
  }, []);

  const save = useCallback((next: string[]) => {
    setSymbols(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, []);

  const add = useCallback(
    (symbol: string) => {
      if (symbols.includes(symbol)) return;
      save([...symbols, symbol]);
    },
    [symbols, save]
  );

  const remove = useCallback(
    (symbol: string) => {
      save(symbols.filter((s) => s !== symbol));
    },
    [symbols, save]
  );

  return { symbols, add, remove, save };
}

export function WatchlistPanel() {
  const { symbols, add, remove } = useWatchlist();
  const [input, setInput] = useState("BTC/USDT");
  const [tf, setTf] = useState("1h");

  const key = symbols.length ? ["watchlist", symbols.join(","), tf] : null;
  const { data, isLoading } = useSWR(key, () => api.analyzeBatch(symbols, tf));

  const results = (data?.results ?? []) as Verdict[];

  return (
    <div className="card space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-lg font-semibold">Watchlist</h2>
        <div className="flex gap-2 text-sm">
          {["15m", "1h", "4h"].map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTf(t)}
              className={`rounded px-2 py-0.5 ${tf === t ? "bg-sky-600" : "bg-slate-800"}`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <input
          className="rounded border border-border bg-slate-900 px-2 py-1 text-sm"
          value={input}
          onChange={(e) => setInput(e.target.value.toUpperCase())}
          placeholder="BTC/USDT"
        />
        <button
          type="button"
          className="rounded bg-sky-700 px-3 py-1 text-sm"
          onClick={() => add(input.trim())}
        >
          Add
        </button>
      </div>
      {symbols.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {symbols.map((s) => (
            <span key={s} className="flex items-center gap-1 rounded-full bg-slate-800 px-2 py-0.5 text-xs">
              <Link href={`/pair/${encodeURIComponent(s)}`} className="text-sky-400 hover:underline">
                {s}
              </Link>
              <button type="button" className="text-muted hover:text-white" onClick={() => remove(s)} aria-label={`Remove ${s}`}>
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      {symbols.length === 0 && <p className="text-sm text-muted">Add pairs to scan only what you care about.</p>}
      {isLoading && symbols.length > 0 && <LoadingCard />}
      {results.length > 0 && <PairTable results={results} />}
    </div>
  );
}
