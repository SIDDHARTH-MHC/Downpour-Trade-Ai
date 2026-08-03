"""Lane 4 — Regime detection and gating."""

from __future__ import annotations

import pandas as pd

from engine.config import EngineConfig, load_config
from engine.indicators import adx_wilder, atr_wilder, ema
from engine.models import RegimeResult
from engine.utils import lookback_bars_for_days


def _atr_percentile(df: pd.DataFrame, lookback_bars: int) -> tuple[float, float]:
    atr_series = atr_wilder(df["high"], df["low"], df["close"], 14) / df["close"]
    recent = float(atr_series.iloc[-1])
    window = atr_series.tail(lookback_bars).dropna()
    if len(window) < 10:
        return recent, 50.0
    percentile = float((window < recent).sum() / len(window) * 100)
    return recent, percentile


def _trend_regime(df_4h: pd.DataFrame) -> str:
    close = df_4h["close"]
    if len(close) < 200:
        return "RANGING"
    adx = float(adx_wilder(df_4h["high"], df_4h["low"], close, 14).iloc[-1])
    e200 = ema(close, 200)
    slope = float(e200.iloc[-1] - e200.iloc[-5]) / float(e200.iloc[-5]) if e200.iloc[-5] else 0.0
    if adx > 25 and slope > 0.001:
        return "TRENDING_UP"
    if adx > 25 and slope < -0.001:
        return "TRENDING_DOWN"
    return "RANGING"


def analyze_regime(
    df: pd.DataFrame,
    df_4h: pd.DataFrame,
    symbol: str,
    btc_df: pd.DataFrame | None = None,
    config: EngineConfig | None = None,
    tf: str = "1h",
    macro: dict | None = None,
) -> RegimeResult:
    cfg = (config or load_config()).regime
    evidence: list[str] = []
    values: dict[str, float] = {}

    lookback_bars = min(len(df) - 1, lookback_bars_for_days(tf, cfg.lookback_days))
    lookback_bars = max(90, lookback_bars)
    atr_ratio, percentile = _atr_percentile(df, lookback_bars)
    values["atr_ratio"] = atr_ratio
    values["atr_percentile"] = percentile

    regime = _trend_regime(df_4h)
    tradeable = True
    evidence.append(f"4h trend regime={regime}")

    if percentile > cfg.shock_percentile:
        regime = "SHOCK"
        tradeable = False
        evidence.append(f"ATR percentile={percentile:.1f} > {cfg.shock_percentile:.0f} → SHOCK, NO-TRADE")
    elif percentile < cfg.compression_percentile:
        regime = "COMPRESSION"
        evidence.append(f"ATR percentile={percentile:.1f} < {cfg.compression_percentile:.0f} → COMPRESSION")

    base = symbol.split("/")[0]
    if base != "BTC" and btc_df is not None and len(btc_df) > 2:
        btc_move = (btc_df["close"].iloc[-1] - btc_df["close"].iloc[-2]) / btc_df["close"].iloc[-2]
        values["btc_1h_move"] = float(btc_move)
        if abs(btc_move) > cfg.btc_move_threshold:
            tradeable = False
            evidence.append(f"BTC 1h move={btc_move*100:.2f}% > ±{cfg.btc_move_threshold*100:.0f}% → alt NO-TRADE")

    weights = dict(
        cfg.weights.get(regime, cfg.weights.get("RANGING", {"technical": 1.0, "flow": 1.0, "structure": 1.0}))
    )

    if cfg.macro_dxy_risk_off_enabled and macro:
        dxy_pct = macro.get("dxy_24h_pct")
        if dxy_pct is not None:
            values["dxy_24h_pct"] = float(dxy_pct)
            if dxy_pct >= cfg.macro_dxy_risk_off_pct:
                evidence.append(
                    f"DXY daily +{dxy_pct*100:.2f}% ≥ {cfg.macro_dxy_risk_off_pct*100:.1f}% → macro risk-off context"
                )
                weights["technical"] = weights.get("technical", 1.0) * 0.85

    if regime == "SHOCK":
        weights = {}

    return RegimeResult(regime=regime, tradeable=tradeable, lane_weights=weights, evidence=evidence, values=values)
