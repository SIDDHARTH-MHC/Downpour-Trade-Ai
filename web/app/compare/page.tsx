"use client";

import { useState } from "react";
import useSWR from "swr";
import Link from "next/link";
import { api } from "@/lib/api";
import { DataStamp, ErrorState, LoadingCard } from "@/components/DisclaimerFooter";

const LANES = ["technical", "flow", "structure"] as const;

export default function ComparePage() {
  const [a, setA] = useState("BTC/USDT");
  const [b, setB] = useState("ETH/USDT");
  const [tf, setTf] = useState("1h");
  const key = ["compare", a, b, tf];
  const { data, error, isLoading, mutate } = useSWR(key, () => api.compare(a, b, tf));

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Compare signals</h1>
        <p className="text-sm text-muted">Side-by-side lane scores and verdicts</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <input className="rounded border border-border bg-slate-900 px-2 py-1 text-sm" value={a} onChange={(e) => setA(e.target.value.toUpperCase())} />
        <span className="self-center text-muted">vs</span>
        <input className="rounded border border-border bg-slate-900 px-2 py-1 text-sm" value={b} onChange={(e) => setB(e.target.value.toUpperCase())} />
        {["1h", "4h"].map((t) => (
          <button key={t} type="button" onClick={() => setTf(t)} className={`rounded px-2 py-1 text-sm ${tf === t ? "bg-sky-600" : "bg-slate-800"}`}>
            {t}
          </button>
        ))}
        <button type="button" className="rounded bg-slate-700 px-3 py-1 text-sm" onClick={() => mutate()}>
          Refresh
        </button>
      </div>
      <DataStamp label={data?.data_as_of_utc} />
      {isLoading && <LoadingCard />}
      {error && <ErrorState message={(error as Error).message} />}
      {data && (
        <div className="grid gap-4 md:grid-cols-2">
          {[data.a, data.b].map((side) => (
            <div key={side.symbol} className="card space-y-2 text-sm">
              <Link href={`/pair/${encodeURIComponent(side.symbol)}`} className="text-lg font-semibold text-sky-400 hover:underline">
                {side.symbol}
              </Link>
              <p>
                {side.action} · score {side.weighted_score.toFixed(1)} · {side.regime}
              </p>
              <p className="text-xs text-muted">{side.confidence}</p>
              <table className="w-full">
                <tbody>
                  {LANES.map((lane) => (
                    <tr key={lane} className="border-t border-border/40">
                      <td className="py-1 capitalize">{lane}</td>
                      <td className="py-1 text-right">{(side.lanes[lane] ?? 0).toFixed(0)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
