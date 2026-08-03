"""Lane 1 — Technical analysis."""

from __future__ import annotations

import pandas as pd

from engine.config import EngineConfig, load_config
from engine.indicators import adx_wilder, ema, macd, rsi_wilder, session_vwap
from engine.models import LaneResult


def _ema_stack_score(close: float, e20: float, e50: float, e200: float, cfg) -> tuple[float, str]:
    if close > e20 > e50 > e200:
        return cfg.ema_stack_bull, f"close>{e20:.2f}>EMA20>EMA50>EMA200 (+{cfg.ema_stack_bull:.0f})"
    if close < e20 < e50 < e200:
        return cfg.ema_stack_bear, f"close<{e20:.2f}<EMA20<EMA50<EMA200 ({cfg.ema_stack_bear:.0f})"
    return 0.0, f"EMA stack mixed (0)"


def _htf_sign(df_htf: pd.DataFrame, cfg) -> int:
    close = df_htf["close"]
    e20 = ema(close, 20).iloc[-1]
    e50 = ema(close, 50).iloc[-1]
    e200 = ema(close, 200).iloc[-1]
    c = close.iloc[-1]
    if c > e20 > e50 > e200:
        return 1
    if c < e20 < e50 < e200:
        return -1
    return 0


def analyze_technical(
    df: pd.DataFrame,
    df_htf: pd.DataFrame | None = None,
    config: EngineConfig | None = None,
) -> LaneResult:
    cfg = (config or load_config()).technical
    close = df["close"]
    high, low = df["high"], df["low"]

    e20 = ema(close, 20).iloc[-1]
    e50 = ema(close, 50).iloc[-1]
    e200 = ema(close, 200).iloc[-1]
    price = close.iloc[-1]

    evidence: list[str] = []
    values: dict[str, float] = {
        "close": float(price),
        "ema20": float(e20),
        "ema50": float(e50),
        "ema200": float(e200),
    }

    stack_score, stack_ev = _ema_stack_score(price, e20, e50, e200, cfg)
    trend_score = stack_score
    evidence.append(stack_ev)

    apply_ema200_side = True
    if cfg.ema200_side_only_when_stack_neutral:
        apply_ema200_side = stack_score == 0.0

    if apply_ema200_side:
        if price > e200:
            trend_score += cfg.ema200_side
            evidence.append(f"close above EMA200={e200:.2f} (+{cfg.ema200_side:.0f})")
        else:
            trend_score -= cfg.ema200_side
            evidence.append(f"close below EMA200={e200:.2f} (-{cfg.ema200_side:.0f})")
    elif stack_score != 0:
        evidence.append("EMA200 side skipped (stack already aligned, orthogonalization)")

    rsi = rsi_wilder(close, 14)
    rsi_val = float(rsi.iloc[-1])
    values["rsi14"] = rsi_val
    oscillator_score = 0.0
    if rsi_val > cfg.rsi_bull_threshold:
        oscillator_score += cfg.rsi_bull
        evidence.append(f"RSI(14)={rsi_val:.1f} → bullish (+{cfg.rsi_bull:.0f})")
    elif rsi_val < cfg.rsi_bear_threshold:
        oscillator_score += cfg.rsi_bear
        evidence.append(f"RSI(14)={rsi_val:.1f} → bearish ({cfg.rsi_bear:.0f})")
    else:
        evidence.append(f"RSI(14)={rsi_val:.1f} → neutral (0)")

    if rsi_val > cfg.rsi_overbought_threshold:
        oscillator_score += cfg.rsi_overbought_penalty
        evidence.append(f"RSI(14)={rsi_val:.1f} overbought penalty ({cfg.rsi_overbought_penalty:.0f})")
    elif rsi_val < cfg.rsi_oversold_threshold:
        oscillator_score += cfg.rsi_oversold_penalty
        evidence.append(f"RSI(14)={rsi_val:.1f} oversold penalty (+{cfg.rsi_oversold_penalty:.0f})")

    _, _, hist = macd(close)
    hist_vals = hist.iloc[-3:]
    values["macd_hist"] = float(hist.iloc[-1])
    macd_bull = (
        len(hist_vals) >= 3
        and hist_vals.iloc[-1] > 0
        and hist_vals.iloc[-1] > hist_vals.iloc[-2] > hist_vals.iloc[-3]
    )
    macd_bear = (
        len(hist_vals) >= 3
        and hist_vals.iloc[-1] < 0
        and hist_vals.iloc[-1] < hist_vals.iloc[-2] < hist_vals.iloc[-3]
    )
    if macd_bull:
        if cfg.macd_requires_stack_agreement and stack_score <= 0:
            evidence.append(f"MACD hist rising — not scored (stack disagreement, orthogonalization)")
        else:
            trend_score += cfg.macd_bull
            evidence.append(f"MACD hist={hist_vals.iloc[-1]:.4f} rising (+{cfg.macd_bull:.0f})")
    elif macd_bear:
        if cfg.macd_requires_stack_agreement and stack_score >= 0:
            evidence.append(f"MACD hist falling — not scored (stack disagreement, orthogonalization)")
        else:
            trend_score += cfg.macd_bear
            evidence.append(f"MACD hist={hist_vals.iloc[-1]:.4f} falling ({cfg.macd_bear:.0f})")
    else:
        evidence.append(f"MACD hist={hist.iloc[-1]:.4f} → neutral (0)")

    adx_val = float(adx_wilder(high, low, close, 14).iloc[-1])
    values["adx14"] = adx_val
    multiplier = 1.0
    if adx_val > cfg.adx_trend_threshold:
        multiplier = cfg.adx_trend_multiplier
        evidence.append(f"ADX(14)={adx_val:.1f} → trend confirmed (×{multiplier})")
    elif adx_val < cfg.adx_chop_threshold:
        multiplier = cfg.adx_chop_multiplier
        evidence.append(f"ADX(14)={adx_val:.1f} → chop (×{multiplier})")
    else:
        evidence.append(f"ADX(14)={adx_val:.1f} → neutral multiplier (×1.0)")

    if cfg.adx_multiplier_scope == "trend_subscore":
        score = trend_score * multiplier + oscillator_score
        if multiplier != 1.0:
            evidence.append("ADX multiplier applied to trend sub-score only (stack/EMA200/MACD)")
    else:
        score = (trend_score + oscillator_score) * multiplier

    if cfg.session_vwap_evidence and len(df) >= 2:
        vwap = session_vwap(df)
        values["session_vwap"] = float(vwap)
        if price >= vwap:
            evidence.append(f"close above UTC session VWAP={vwap:.2f} (evidence)")
        else:
            evidence.append(f"close below UTC session VWAP={vwap:.2f} (evidence)")

    if df_htf is not None and len(df_htf) >= 200:
        htf_sign = _htf_sign(df_htf, cfg)
        ltf_sign = 1 if score > 0 else (-1 if score < 0 else 0)
        if htf_sign != 0 and ltf_sign != 0 and htf_sign != ltf_sign:
            score *= 0.5
            evidence.append("HTF EMA stack disagrees with LTF → score halved (×0.5)")

    score = max(-100.0, min(100.0, score))
    return LaneResult(name="technical", score=score, evidence=evidence, values=values)
