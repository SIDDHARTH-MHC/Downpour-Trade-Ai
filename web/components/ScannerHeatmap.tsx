import Link from "next/link";
import { Verdict } from "@/lib/api";

function cellClass(action: Verdict["action"]) {
  if (action === "LONG") return "bg-long/25 text-long border-long/40";
  if (action === "SHORT") return "bg-short/25 text-short border-short/40";
  return "bg-slate-800/80 text-muted border-border";
}

export function ScannerHeatmap({ results }: { results: Verdict[] }) {
  if (!results.length) {
    return <p className="text-sm text-muted">No scan data for heatmap.</p>;
  }

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5">
      {results.map((row) => (
        <Link
          key={row.symbol}
          href={`/pair/${encodeURIComponent(row.symbol)}`}
          className={`rounded border px-2 py-3 text-center text-xs transition hover:opacity-90 ${cellClass(row.action)}`}
        >
          <div className="font-semibold">{row.symbol.replace("/USDT", "")}</div>
          <div>{row.action}</div>
          <div className="text-[10px] opacity-80">{row.weighted_score.toFixed(0)}</div>
        </Link>
      ))}
    </div>
  );
}
