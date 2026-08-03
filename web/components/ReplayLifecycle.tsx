import { LifecycleState, ReplayEvent } from "@/lib/api";

export function ReplayTimeline({ events }: { events: ReplayEvent[] }) {
  if (!events.length) {
    return <p className="text-sm text-muted">No replay events for this verdict.</p>;
  }

  return (
    <ol className="relative border-l border-border pl-4">
      {events.map((ev) => (
        <li key={ev.step} className="mb-4 ml-1">
          <span className="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full bg-sky-600" />
          <p className="text-xs uppercase text-muted">{ev.category}</p>
          <p className="text-sm">{ev.label}</p>
        </li>
      ))}
    </ol>
  );
}

export function LifecycleStepper({ lifecycle }: { lifecycle?: LifecycleState }) {
  if (!lifecycle || lifecycle.stage === "none") return null;

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">Signal lifecycle</h3>
      <p className="text-xs text-muted">Current: {lifecycle.label}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {lifecycle.steps.map((step) => (
          <span
            key={step.id}
            className={`rounded-full px-2 py-0.5 text-xs ${
              step.status === "current"
                ? "bg-sky-600 text-white"
                : step.status === "done"
                  ? "bg-slate-700 text-muted"
                  : "border border-border text-muted"
            }`}
          >
            {step.label}
          </span>
        ))}
      </div>
    </div>
  );
}
