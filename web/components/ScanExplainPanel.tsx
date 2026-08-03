import { ScanReport } from "@/lib/api";

const LABELS: Record<string, string> = {
  regime_block: "Regime / BTC gate",
  lane_conflict: "Lane conflict",
  structure_no_edge: "Structure no edge",
  weak_alignment: "Lanes not aligned",
  adverse_lane: "Adverse lane",
  score_neutral: "Score in neutral band",
  other: "Other",
};

export function ScanExplainPanel({ report }: { report?: ScanReport | null }) {
  if (!report) {
    return (
      <div className="card text-sm text-muted">
        Scan explainability appears after the next full scan completes.
      </div>
    );
  }

  const entries = Object.entries(report.rejection_reasons || {}).sort((a, b) => b[1] - a[1]);

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">Why coins were rejected</h3>
      <p className="text-xs text-muted">
        {report.rejected_count} NO_TRADE of {report.total_scanned} scanned · {report.actionable_count}{" "}
        actionable
      </p>
      {entries.length > 0 ? (
        <ul className="mt-3 space-y-2 text-sm">
          {entries.map(([key, count]) => (
            <li key={key} className="flex justify-between gap-4">
              <span>{LABELS[key] || key}</span>
              <span className="text-muted">{count}</span>
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-2 text-sm text-muted">No rejection histogram yet.</p>
      )}
    </div>
  );
}
