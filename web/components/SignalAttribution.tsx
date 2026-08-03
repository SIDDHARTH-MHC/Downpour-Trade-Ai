import { Verdict } from "@/lib/api";

const LABELS: Record<string, string> = {
  technical: "Technical",
  flow: "Flow",
  structure: "Structure",
};

const ORDER = ["technical", "flow", "structure"] as const;

function barColor(name: string) {
  if (name === "technical") return "bg-sky-500";
  if (name === "flow") return "bg-violet-500";
  return "bg-amber-500";
}

function fallbackAttribution(verdict: Verdict): Record<string, number> {
  const names = ["technical", "flow", "structure"] as const;
  const weights = verdict.regime.lane_weights || {};
  let total = 0;
  const parts: Record<string, number> = {};
  for (const name of names) {
    const lane = verdict.lanes.find((l) => l.name === name);
    const w = weights[name] ?? 1;
    const c = Math.abs(lane?.score ?? 0) * w;
    parts[name] = c;
    total += c;
  }
  if (total <= 0) return { technical: 1 / 3, flow: 1 / 3, structure: 1 / 3 };
  return Object.fromEntries(names.map((n) => [n, parts[n] / total]));
}

export function SignalAttribution({ verdict }: { verdict: Verdict }) {
  const attr = verdict.attribution ?? fallbackAttribution(verdict);
  const lanes = verdict.lanes.filter((l) => ORDER.includes(l.name as (typeof ORDER)[number]));

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">Signal attribution</h3>
      <p className="text-xs text-muted">Share of weighted lane magnitude (regime weights applied)</p>
      <div className="mt-4 space-y-3">
        {ORDER.map((name) => {
          const lane = lanes.find((l) => l.name === name);
          const share = attr?.[name] ?? 0;
          const pct = Math.round(share * 100);
          return (
            <div key={name}>
              <div className="mb-1 flex justify-between text-xs">
                <span>{LABELS[name]}</span>
                <span className="text-muted">
                  score {lane?.score.toFixed(0) ?? "—"} · {pct}%
                </span>
              </div>
              <div className="h-2 overflow-hidden rounded bg-slate-800">
                <div className={`h-full ${barColor(name)}`} style={{ width: `${Math.max(pct, 4)}%` }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
