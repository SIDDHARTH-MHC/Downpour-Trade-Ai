import { Verdict } from "@/lib/api";

export function TradePlanBox({ plan }: { plan: NonNullable<Verdict["trade_plan"]> }) {
  return (
    <div className="card border-long/30">
      <h3 className="mb-3 font-semibold">Trade plan</h3>
      <div className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
        <div><span className="text-muted">Entry</span><div>{plan.entry}</div></div>
        <div><span className="text-muted">SL</span><div className="text-short">{plan.stop_loss}</div></div>
        <div><span className="text-muted">TP1</span><div className="text-long">{plan.tp1}</div></div>
        <div><span className="text-muted">TP2</span><div className="text-long">{plan.tp2}</div></div>
        <div><span className="text-muted">R:R</span><div>{plan.reward_risk.toFixed(2)}</div></div>
        <div><span className="text-muted">Size</span><div>{plan.size_coin.toFixed(6)}</div></div>
        <div><span className="text-muted">USD</span><div>${plan.size_usd.toFixed(2)}</div></div>
      </div>
    </div>
  );
}
