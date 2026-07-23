import Link from "next/link";
import { Verdict } from "@/lib/api";
import { RegimeBadge } from "./RegimeBadge";

function VerdictChip({ action }: { action: Verdict["action"] }) {
  const cls =
    action === "LONG"
      ? "bg-long/20 text-long"
      : action === "SHORT"
        ? "bg-short/20 text-short"
        : "bg-slate-700 text-muted";
  return <span className={`rounded px-2 py-0.5 text-xs font-semibold ${cls}`}>{action}</span>;
}

export function PairTable({ results }: { results: Verdict[] }) {
  return (
    <div className="overflow-x-auto card">
      <table className="min-w-full text-sm">
        <thead className="text-left text-muted">
          <tr>
            <th className="pb-2">Pair</th>
            <th className="pb-2">Regime</th>
            <th className="pb-2">Score</th>
            <th className="pb-2">Verdict</th>
          </tr>
        </thead>
        <tbody>
          {results.map((row) => (
            <tr key={row.symbol} className="border-t border-border/60">
              <td className="py-2">
                <Link className="text-sky-400 hover:underline" href={`/pair/${encodeURIComponent(row.symbol)}`}>
                  {row.symbol}
                </Link>
              </td>
              <td className="py-2">
                <RegimeBadge regime={row.regime.name} tradeable={row.regime.tradeable} />
              </td>
              <td className="py-2">{row.weighted_score.toFixed(1)}</td>
              <td className="py-2"><VerdictChip action={row.action} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
