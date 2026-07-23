import { Verdict } from "@/lib/api";

export function LanePanel({ lanes }: { lanes: Verdict["lanes"] }) {
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {lanes.map((lane) => (
        <div key={lane.name} className="card">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="font-medium capitalize">{lane.name}</h3>
            <span className={lane.score >= 0 ? "text-long" : "text-short"}>
              {lane.score >= 0 ? "+" : ""}
              {lane.score.toFixed(1)}
            </span>
          </div>
          <div className="mb-2 h-2 overflow-hidden rounded bg-slate-800">
            <div
              className={`h-full ${lane.score >= 0 ? "bg-long" : "bg-short"}`}
              style={{ width: `${Math.min(100, Math.abs(lane.score))}%` }}
            />
          </div>
          <ul className="space-y-1 text-xs text-muted">
            {lane.evidence.map((line, i) => (
              <li key={i}>{line}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
