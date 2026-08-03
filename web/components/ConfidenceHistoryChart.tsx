import { ConfidencePoint } from "@/lib/api";

export function ConfidenceHistoryChart({ points }: { points: ConfidencePoint[] }) {
  if (points.length === 0) {
    return <p className="text-sm text-muted">No LONG/SHORT history yet for this filter.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="text-left text-muted">
          <tr>
            <th className="pb-2 pr-4">Time</th>
            <th className="pb-2 pr-4">Pair</th>
            <th className="pb-2 pr-4">Action</th>
            <th className="pb-2 pr-4">Score</th>
            <th className="pb-2 pr-4">Confidence</th>
            <th className="pb-2">Outcome</th>
          </tr>
        </thead>
        <tbody>
          {points.map((p, i) => (
            <tr key={i} className="border-t border-border/60">
              <td className="py-2 pr-4 whitespace-nowrap">{p.timestamp}</td>
              <td className="py-2 pr-4">{p.symbol}</td>
              <td className="py-2 pr-4">{p.action}</td>
              <td className="py-2 pr-4">{p.weighted_score.toFixed(1)}</td>
              <td className="py-2 pr-4 max-w-xs truncate">{p.confidence}</td>
              <td className="py-2">
                <OutcomeBadge outcome={p.outcome} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function OutcomeBadge({ outcome }: { outcome: string | null | undefined }) {
  if (!outcome) return <span className="text-muted">—</span>;
  const cls =
    outcome === "WIN"
      ? "text-long"
      : outcome === "LOSS"
        ? "text-short"
        : outcome === "OPEN"
          ? "text-amber-400"
          : "text-muted";
  return <span className={cls}>{outcome}</span>;
}
