import { Verdict } from "@/lib/api";

export function StructureEventsPanel({ events }: { events: Verdict["structure_events"] }) {
  if (!events?.length) {
    return (
      <div className="card text-sm text-muted">
        <h3 className="font-semibold text-white">Structure (BOS / CHoCH)</h3>
        <p className="mt-2">No break or character change detected on the latest bar.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-sm font-semibold">Structure (BOS / CHoCH)</h3>
      <ul className="mt-3 space-y-2 text-sm">
        {events.map((ev, i) => (
          <li
            key={i}
            className={`rounded border px-3 py-2 ${
              ev.direction === "bullish" ? "border-long/30 text-long" : "border-short/30 text-short"
            }`}
          >
            <span className="font-medium">{ev.type}</span> · {ev.label}
          </li>
        ))}
      </ul>
    </div>
  );
}
