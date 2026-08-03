"use client";

import { useCallback, useEffect, useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { api, Verdict } from "@/lib/api";
import { PairTable } from "@/components/PairTable";
import { LoadingCard } from "@/components/DisclaimerFooter";
import { EmptyState } from "@/components/shell/EmptyState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { WATCHLIST_STORAGE_KEY } from "@/lib/watchlist-prefs";
import { Star } from "lucide-react";

export function useWatchlist() {
  const [symbols, setSymbols] = useState<string[]>([]);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(WATCHLIST_STORAGE_KEY);
      if (raw) setSymbols(JSON.parse(raw) as string[]);
    } catch {
      setSymbols([]);
    }
  }, []);

  const save = useCallback((next: string[]) => {
    setSymbols(next);
    localStorage.setItem(WATCHLIST_STORAGE_KEY, JSON.stringify(next));
  }, []);

  const add = useCallback(
    (symbol: string) => {
      if (symbols.includes(symbol)) return;
      save([...symbols, symbol].slice(0, 8));
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
        <div className="flex gap-1">
          {["15m", "1h", "4h"].map((t) => (
            <Button key={t} type="button" size="sm" variant={tf === t ? "default" : "outline"} onClick={() => setTf(t)}>
              {t}
            </Button>
          ))}
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <Input
          className="h-8 max-w-[10rem]"
          value={input}
          onChange={(e) => setInput(e.target.value.toUpperCase())}
          placeholder="BTC/USDT"
          aria-label="Watchlist symbol"
        />
        <Button type="button" size="sm" onClick={() => add(input.trim())}>
          Add
        </Button>
      </div>
      {symbols.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {symbols.map((s) => (
            <span key={s} className="flex items-center gap-1 rounded-full bg-muted px-2 py-0.5 text-xs">
              <Link href={`/pair/${encodeURIComponent(s)}`} className="text-primary underline-offset-2 hover:underline">
                {s}
              </Link>
              <button
                type="button"
                className="text-muted-foreground hover:text-foreground"
                onClick={() => remove(s)}
                aria-label={`Remove ${s}`}
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
      {symbols.length === 0 && (
        <EmptyState
          icon={Star}
          title="No pinned pairs"
          description="Add symbols to batch-analyze only what you care about. Pins also appear in the sidebar and command palette."
          className="border-none bg-transparent p-0 shadow-none [&>div]:py-4"
        />
      )}
      {isLoading && symbols.length > 0 && <LoadingCard />}
      {results.length > 0 && <PairTable results={results} />}
    </div>
  );
}
