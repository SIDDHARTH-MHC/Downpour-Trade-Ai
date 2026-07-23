import { Verdict } from "@/lib/api";
import { RegimeBadge } from "./RegimeBadge";

export function VerdictCard({ verdict }: { verdict: Verdict }) {
  const actionColor =
    verdict.action === "LONG"
      ? "text-long border-long/40"
      : verdict.action === "SHORT"
        ? "text-short border-short/40"
        : "text-muted border-border";

  return (
    <div className={`card border ${actionColor}`}>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-semibold">{verdict.symbol}</h2>
          <p className="text-sm text-muted">
            {verdict.timeframe} · {verdict.timestamp}
          </p>
        </div>
        <div className="text-right">
          <div className={`text-2xl font-bold ${actionColor.split(" ")[0]}`}>{verdict.action}</div>
          <div className="text-sm">score {verdict.weighted_score.toFixed(1)}</div>
        </div>
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        <RegimeBadge regime={verdict.regime.name} tradeable={verdict.regime.tradeable} />
        <span className="rounded-full bg-slate-800 px-2 py-0.5 text-xs">{verdict.confidence}</span>
      </div>
      {verdict.reasons?.length > 0 && (
        <p className="mt-3 text-sm text-muted">{verdict.reasons.join(" · ")}</p>
      )}
    </div>
  );
}
