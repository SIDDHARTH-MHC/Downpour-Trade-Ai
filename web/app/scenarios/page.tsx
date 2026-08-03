"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { ErrorState, LoadingCard } from "@/components/DisclaimerFooter";
import { ModuleHeader } from "@/components/shell/ModuleHeader";
import { Button } from "@/components/ui/button";

export default function ScenariosPage() {
  const [shockPct, setShockPct] = useState(-5);
  const [result, setResult] = useState<Awaited<ReturnType<typeof api.runScenario>> | null>(null);
  const [running, setRunning] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  async function run() {
    setRunning(true);
    setErr(null);
    try {
      const res = await api.runScenario({ shock_pct: shockPct / 100, shock_asset: "BTC", tf: "1h" });
      setResult(res);
    } catch (e) {
      setErr((e as Error).message);
    } finally {
      setRunning(false);
    }
  }

  return (
    <div className="space-y-4">
      <ModuleHeader title="Scenario simulator" description="Stress open tracked signals — heuristic beta vs BTC" />
      <div className="card flex flex-wrap items-end gap-3">
        <label className="text-sm">
          BTC shock (%)
          <input
            type="number"
            className="ml-2 w-24 rounded border border-border bg-slate-900 px-2 py-1"
            value={shockPct}
            onChange={(e) => setShockPct(Number(e.target.value))}
          />
        </label>
        <button type="button" onClick={run} disabled={running} className="rounded bg-sky-600 px-4 py-2 text-sm disabled:opacity-50">
          {running ? "Running…" : "Run scenario"}
        </button>
      </div>
      {err && <ErrorState message={err} />}
      {result && (
        <div className="card overflow-x-auto text-sm">
          <p className="mb-2 text-muted">
            {result.open_positions} open positions · shock {result.shock_pct * 100}% on {result.shock_asset}
          </p>
          <table className="min-w-full">
            <thead className="text-left text-muted">
              <tr>
                <th className="pb-2">Symbol</th>
                <th className="pb-2">Move</th>
                <th className="pb-2">Shocked</th>
                <th className="pb-2">SL hit</th>
                <th className="pb-2">TP1 hit</th>
              </tr>
            </thead>
            <tbody>
              {result.positions.map((p, i) => (
                <tr key={i} className="border-t border-border/60">
                  <td className="py-2">{p.symbol}</td>
                  <td className="py-2">{p.move_pct}%</td>
                  <td className="py-2">{p.shocked_price}</td>
                  <td className="py-2">{p.sl_hit ? "yes" : "no"}</td>
                  <td className="py-2">{p.tp1_hit ? "yes" : "no"}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {result.positions.length === 0 && <p className="text-muted">No open signals with trade plans.</p>}
          <p className="mt-3 text-xs text-muted">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
