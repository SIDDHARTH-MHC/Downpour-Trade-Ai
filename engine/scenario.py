"""Stress shock on open tracked signals (context only — not a trading recommendation)."""

from __future__ import annotations

from typing import Any

from engine.correlation import correlation_vs_btc


def simulate_shock(
    open_positions: list[dict[str, Any]],
    *,
    shock_asset: str = "BTC",
    shock_pct: float = -0.05,
    tf: str = "1h",
) -> dict[str, Any]:
    """
    Apply a simple shock: alts move shock_pct * beta_vs_btc; BTC moves shock_pct.
    Mark SL/TP hit on shocked price vs entry.
    """
    results = []
    for item in open_positions:
        payload = item.get("payload") or item
        plan = payload.get("trade_plan")
        if not plan:
            continue
        symbol = payload.get("symbol", "")
        action = payload.get("action")
        entry = float(plan["entry"])
        sl = float(plan["stop_loss"])
        tp1 = float(plan["tp1"])

        if shock_asset == "BTC" and symbol.startswith("BTC/"):
            move = shock_pct
        elif shock_asset == "BTC":
            corr = correlation_vs_btc(symbol, tf=tf)
            beta = corr.get("beta_vs_btc") or corr.get("correlation") or 1.0
            move = shock_pct * float(beta)
        else:
            base = symbol.split("/")[0]
            move = shock_pct if base == shock_asset else shock_pct * 0.5

        shocked = entry * (1 + move)
        hit_sl = (action == "LONG" and shocked <= sl) or (action == "SHORT" and shocked >= sl)
        hit_tp = (action == "LONG" and shocked >= tp1) or (action == "SHORT" and shocked <= tp1)

        results.append(
            {
                "symbol": symbol,
                "action": action,
                "entry": entry,
                "shocked_price": round(shocked, 6),
                "move_pct": round(move * 100, 2),
                "stop_loss": sl,
                "tp1": tp1,
                "sl_hit": hit_sl,
                "tp1_hit": hit_tp,
                "verdict_id": item.get("verdict_id"),
            }
        )

    return {
        "shock_asset": shock_asset,
        "shock_pct": shock_pct,
        "positions": results,
        "disclaimer": "Heuristic shock model for open signals only — not portfolio advice.",
    }
