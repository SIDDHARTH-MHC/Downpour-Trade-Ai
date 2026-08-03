"use client";

import useSWR from "swr";
import { api } from "@/lib/api";

export function LiquiditySnapshotPanel({ symbol }: { symbol: string }) {
  const { data, error, isLoading } = useSWR(["liq", symbol], () => api.liquiditySnapshot(symbol), {
    refreshInterval: 120_000,
  });

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">Liquidity snapshot</h3>
      <p className="text-xs text-muted">Current book — not historical replay</p>
      {isLoading && <p className="mt-2 text-sm text-muted">Loading book…</p>}
      {error && <p className="mt-2 text-sm text-red-400">{(error as Error).message}</p>}
      {data && (
        <>
          <p className="mt-2 text-sm">Mid: {data.mid_price.toFixed(4)}</p>
          {data.walls.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium text-muted">Detected walls</p>
              <ul className="text-sm">
                {data.walls.map((w, i) => (
                  <li key={i}>
                    {w.side} @ {w.price.toFixed(2)} (${(w.notional_usd / 1e6).toFixed(2)}M)
                  </li>
                ))}
              </ul>
            </div>
          )}
        </>
      )}
    </div>
  );
}
