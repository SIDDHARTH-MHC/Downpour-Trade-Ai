"""Entry, stop-loss, take-profit, and position sizing."""

from __future__ import annotations

import pandas as pd

from engine.config import EngineConfig, load_config
from engine.indicators import atr_wilder
from engine.models import TradePlan, Verdict


def build_trade_plan(
    verdict: Verdict,
    df: pd.DataFrame,
    *,
    patient: bool = False,
    equity_usd: float | None = None,
    mid_price: float | None = None,
    config: EngineConfig | None = None,
) -> Verdict:
    cfg = (config or load_config()).risk
    if verdict.action == "NO_TRADE":
        return verdict

    price = mid_price if mid_price is not None else float(df["close"].iloc[-1])
    atr = float(atr_wilder(df["high"], df["low"], df["close"], 14).iloc[-1])
    structure = next((lane for lane in verdict.lanes if lane.name == "structure"), None)
    nearest_support = structure.values.get("nearest_support") if structure else None
    nearest_resistance = structure.values.get("nearest_resistance") if structure else None

    entry = price
    if patient:
        if verdict.action == "LONG" and nearest_support:
            entry = float(nearest_support)
        elif verdict.action == "SHORT" and nearest_resistance:
            entry = float(nearest_resistance)

    if verdict.action == "LONG":
        sl_atr = entry - cfg.atr_sl_multiplier * atr
        if nearest_support and nearest_support > sl_atr:
            stop_loss = nearest_support - cfg.support_sl_buffer_atr * atr
        else:
            stop_loss = sl_atr
        risk = entry - stop_loss
        tp1 = float(nearest_resistance) if nearest_resistance and nearest_resistance > entry else entry + 2 * risk
        tp2 = entry + cfg.tp2_rr_multiplier * risk
    else:
        sl_atr = entry + cfg.atr_sl_multiplier * atr
        if nearest_resistance and nearest_resistance < sl_atr:
            stop_loss = nearest_resistance + cfg.support_sl_buffer_atr * atr
        else:
            stop_loss = sl_atr
        risk = stop_loss - entry
        tp1 = float(nearest_support) if nearest_support and nearest_support < entry else entry - 2 * risk
        tp2 = entry - cfg.tp2_rr_multiplier * risk

    if risk <= 0:
        verdict.action = "NO_TRADE"
        verdict.trade_plan = None
        verdict.reasons.append("invalid risk distance → downgraded to NO-TRADE")
        return verdict

    reward = abs(tp1 - entry)
    rr = reward / risk
    if rr < cfg.min_reward_risk:
        verdict.action = "NO_TRADE"
        verdict.trade_plan = None
        verdict.reasons.append(f"R:R to TP1={rr:.2f} < {cfg.min_reward_risk:.1f} → downgraded to NO-TRADE")
        return verdict

    equity = equity_usd or cfg.default_equity_usd
    account_risk = equity * cfg.account_risk_pct
    size_coin = account_risk / risk
    size_usd = size_coin * entry

    verdict.trade_plan = TradePlan(
        entry=entry,
        stop_loss=stop_loss,
        tp1=tp1,
        tp2=tp2,
        reward_risk=rr,
        size_coin=size_coin,
        size_usd=size_usd,
        patient=patient,
    )
    return verdict
