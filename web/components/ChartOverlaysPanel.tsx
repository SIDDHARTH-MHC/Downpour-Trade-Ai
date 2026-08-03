import { Verdict } from "@/lib/api";

export function ChartOverlaysPanel({ verdict }: { verdict: Verdict }) {
  const structure = verdict.lanes.find((l) => l.name === "structure");
  const values = structure?.values ?? {};
  const levels: Array<{ label: string; price: number | undefined }> = [
    { label: "POC", price: values.poc },
    { label: "Nearest support", price: values.nearest_support },
    { label: "Nearest resistance", price: values.nearest_resistance },
  ];

  for (const ev of verdict.structure_events || []) {
    if (ev.level != null) {
      levels.push({ label: `${ev.type} ${ev.direction}`, price: ev.level });
    }
  }

  const plan = verdict.trade_plan;
  if (plan) {
    levels.push(
      { label: "Entry", price: plan.entry },
      { label: "Stop loss", price: plan.stop_loss },
      { label: "TP1", price: plan.tp1 },
      { label: "TP2", price: plan.tp2 }
    );
  }

  const shown = levels.filter((l) => l.price != null && !Number.isNaN(l.price));

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">Chart overlays (reference levels)</h3>
      <p className="text-xs text-muted">Plot on TradingView — engine-derived, not auto-drawn on embed</p>
      {shown.length === 0 ? (
        <p className="mt-2 text-sm text-muted">No levels for this verdict.</p>
      ) : (
        <ul className="mt-3 space-y-1 text-sm font-mono">
          {shown.map((l, i) => (
            <li key={i} className="flex justify-between gap-4 border-b border-border/30 py-1">
              <span className="text-muted">{l.label}</span>
              <span>{Number(l.price).toFixed(4)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
