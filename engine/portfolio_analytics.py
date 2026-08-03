"""Aggregate risk exposure from open tracked signals."""

from __future__ import annotations

from typing import Any

from engine.config import EngineConfig, load_config


def portfolio_analytics(open_positions: list[dict[str, Any]], equity_usd: float, config: EngineConfig | None = None) -> dict:
    cfg = (config or load_config()).risk
    risk_pct = cfg.account_risk_pct
    per_trade_usd = equity_usd * risk_pct

    longs = shorts = 0
    total_risk_usd = 0.0
    rr_sum = 0.0
    rr_n = 0
    rows = []

    for item in open_positions:
        payload = item.get("payload") or item
        plan = payload.get("trade_plan")
        if not plan:
            continue
        action = payload.get("action")
        if action == "LONG":
            longs += 1
        elif action == "SHORT":
            shorts += 1
        else:
            continue
        total_risk_usd += per_trade_usd
        rr = float(plan.get("reward_risk") or 0)
        if rr > 0:
            rr_sum += rr
            rr_n += 1
        rows.append(
            {
                "symbol": payload.get("symbol"),
                "action": action,
                "risk_usd": round(per_trade_usd, 2),
                "reward_risk": rr,
                "entry": plan.get("entry"),
                "stop_loss": plan.get("stop_loss"),
            }
        )

    heat_pct = (total_risk_usd / equity_usd * 100) if equity_usd > 0 else 0.0
    return {
        "equity_usd": equity_usd,
        "account_risk_pct_per_trade": risk_pct,
        "open_trades": len(rows),
        "long_count": longs,
        "short_count": shorts,
        "total_risk_usd": round(total_risk_usd, 2),
        "portfolio_heat_pct": round(heat_pct, 2),
        "avg_reward_risk": round(rr_sum / rr_n, 2) if rr_n else None,
        "positions": rows,
        "disclaimer": "Assumes each open signal uses full 1% risk — illustrative only.",
    }
