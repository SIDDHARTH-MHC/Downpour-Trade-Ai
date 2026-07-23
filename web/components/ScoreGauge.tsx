export function ScoreGauge({ score }: { score: number }) {
  const pct = Math.max(-100, Math.min(100, score));
  const left = pct < 0 ? 50 + pct / 2 : 50;
  const width = Math.abs(pct) / 2;
  return (
    <div className="card">
      <div className="mb-2 text-sm text-muted">Weighted score</div>
      <div className="relative h-4 overflow-hidden rounded bg-slate-800">
        <div className="absolute left-1/2 top-0 h-full w-px bg-slate-500" />
        <div
          className={`absolute top-0 h-full ${pct >= 0 ? "bg-long" : "bg-short"}`}
          style={{ left: `${left}%`, width: `${width}%` }}
        />
      </div>
      <div className="mt-2 text-center text-2xl font-bold">{score.toFixed(1)}</div>
    </div>
  );
}
