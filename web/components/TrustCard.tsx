import { TrustResponse } from "@/lib/api";

function fmtPct(v: number | null | undefined) {
  if (v == null || Number.isNaN(v)) return "—";
  return `${(v * 100).toFixed(1)}%`;
}

function fmtNum(v: number | null | undefined, digits = 2) {
  if (v == null || Number.isNaN(v)) return "—";
  return v.toFixed(digits);
}

export function TrustCard({ trust, loading }: { trust?: TrustResponse["trust"]; loading?: boolean }) {
  if (loading) {
    return <div className="card animate-pulse text-sm text-muted">Loading trust metrics…</div>;
  }
  if (!trust) return null;

  const wf =
    trust.walk_forward_passed === null
      ? "—"
      : trust.walk_forward_passed
        ? "Passed"
        : "Failed";

  return (
    <div className="card border border-sky-900/50 bg-slate-900/40">
      <h3 className="text-sm font-semibold text-sky-300">Provable confidence</h3>
      <p className="mt-1 text-xs text-muted">From walk-forward calibration — not marketing tiers</p>
      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 text-sm sm:grid-cols-4">
        <div>
          <dt className="text-muted">Confidence</dt>
          <dd className="font-medium">{trust.confidence}</dd>
        </div>
        <div>
          <dt className="text-muted">Historical win rate</dt>
          <dd className="font-medium">{fmtPct(trust.historical_win_rate)}</dd>
        </div>
        <div>
          <dt className="text-muted">Backtested trades</dt>
          <dd className="font-medium">{trust.backtested_trades ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-muted">Profit factor</dt>
          <dd className="font-medium">{fmtNum(trust.profit_factor)}</dd>
        </div>
        <div>
          <dt className="text-muted">Average R</dt>
          <dd className="font-medium">{fmtNum(trust.average_r)}</dd>
        </div>
        <div>
          <dt className="text-muted">Max drawdown (R)</dt>
          <dd className="font-medium">{fmtNum(trust.max_drawdown_r)}</dd>
        </div>
        <div>
          <dt className="text-muted">Walk-forward</dt>
          <dd className="font-medium">{wf}</dd>
        </div>
        <div>
          <dt className="text-muted">Last calibrated</dt>
          <dd className="font-medium text-xs">{trust.last_calibrated_utc}</dd>
        </div>
      </dl>
      {trust.score_bucket && (
        <p className="mt-2 text-xs text-muted">Score bucket: {trust.score_bucket}</p>
      )}
    </div>
  );
}
