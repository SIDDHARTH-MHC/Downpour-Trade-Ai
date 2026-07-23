"""Lane 2 — Flow / derivatives."""

from __future__ import annotations

import pandas as pd

from engine.config import EngineConfig, load_config
from engine.models import LaneResult


def _funding_score(rate: float | None, cfg) -> tuple[float, str]:
    if rate is None:
        return 0.0, "funding unavailable (0)"
    pct = rate * 100
    if rate < cfg.funding_neutral_low:
        return cfg.funding_short_crowd, f"funding={pct:.4f}% shorts pay longs (+{cfg.funding_short_crowd:.0f})"
    if rate > cfg.funding_crowd_long:
        return cfg.funding_long_crowd, f"funding={pct:.4f}% crowd long ({cfg.funding_long_crowd:.0f})"
    return 0.0, f"funding={pct:.4f}% neutral (0)"


def _funding_trend(history: list[dict], price_change: float, cfg) -> tuple[float, str]:
    if len(history) < 3:
        return 0.0, "funding trend insufficient data (0)"
    rates = [h.get("fundingRate", 0) for h in history[-8:]]
    ma_recent = sum(rates[-3:]) / 3
    ma_prior = sum(rates[:3]) / 3
    if ma_recent < ma_prior and abs(price_change) < 0.005:
        return cfg.funding_trend, f"funding MA falling ({ma_recent:.6f}<{ma_prior:.6f}) w/ flat price (+{cfg.funding_trend:.0f})"
    return 0.0, f"funding trend neutral (0)"


def _oi_price_score(oi_change: float, price_change: float, cfg) -> tuple[float, str]:
    if oi_change > 0 and price_change > 0:
        return cfg.oi_price_new_longs, f"OI +{oi_change*100:.1f}% w/ price +{price_change*100:.1f}% → new longs (+{cfg.oi_price_new_longs:.0f})"
    if oi_change > 0 and price_change < 0:
        return cfg.oi_price_new_shorts, f"OI +{oi_change*100:.1f}% w/ price {price_change*100:.1f}% → new shorts ({cfg.oi_price_new_shorts:.0f})"
    if oi_change < 0 and price_change > 0:
        return cfg.oi_price_short_cover, f"OI {oi_change*100:.1f}% w/ price +{price_change*100:.1f}% → short cover ({cfg.oi_price_short_cover:.0f})"
    if oi_change < 0 and price_change < 0:
        return cfg.oi_price_long_flush, f"OI {oi_change*100:.1f}% w/ price {price_change*100:.1f}% → long flush (+{cfg.oi_price_long_flush:.0f})"
    return 0.0, f"OI/price neutral (0)"


def _taker_score(trades: list[dict], cfg) -> tuple[float, str]:
    if not trades:
        return 0.0, "taker data unavailable (0)"
    buy_vol = sum(t.get("amount", 0) for t in trades if t.get("side") == "buy")
    total = sum(t.get("amount", 0) for t in trades)
    if total <= 0:
        return 0.0, "taker volume zero (0)"
    ratio = buy_vol / total
    if ratio > cfg.taker_bull_ratio:
        return cfg.taker_bull, f"taker buy ratio={ratio:.2f} (+{cfg.taker_bull:.0f})"
    if ratio < cfg.taker_bear_ratio:
        return cfg.taker_bear, f"taker buy ratio={ratio:.2f} ({cfg.taker_bear:.0f})"
    return 0.0, f"taker buy ratio={ratio:.2f} neutral (0)"


def analyze_flow(
    df: pd.DataFrame,
    funding: dict,
    oi_df: pd.DataFrame,
    trades: list[dict] | None = None,
    config: EngineConfig | None = None,
) -> LaneResult:
    cfg = (config or load_config()).flow
    evidence: list[str] = []
    values: dict[str, float] = {}
    score = 0.0

    current = funding.get("current") or {}
    rate = current.get("fundingRate")
    fs, fe = _funding_score(rate, cfg)
    score += fs
    evidence.append(fe)
    if rate is not None:
        values["funding_rate"] = float(rate)

    price_change = (df["close"].iloc[-1] - df["close"].iloc[-24]) / df["close"].iloc[-24] if len(df) > 24 else 0.0
    ft, fte = _funding_trend(funding.get("history", []), price_change, cfg)
    score += ft
    evidence.append(fte)

    oi_change = 0.0
    if len(oi_df) >= 24 and "openInterestValue" in oi_df.columns:
        oi_start = float(oi_df["openInterestValue"].iloc[-24])
        oi_end = float(oi_df["openInterestValue"].iloc[-1])
        if oi_start > 0:
            oi_change = (oi_end - oi_start) / oi_start
            values["oi_change_24h"] = oi_change
            os_score, os_ev = _oi_price_score(oi_change, price_change, cfg)
            if abs(oi_change) > cfg.oi_spike_threshold:
                os_score *= cfg.oi_spike_multiplier
                os_ev += f" · OI spike ×{cfg.oi_spike_multiplier}"
            score += os_score
            evidence.append(os_ev)
    else:
        evidence.append("OI history unavailable (0)")

    ts, te = _taker_score(trades or [], cfg)
    score += ts
    evidence.append(te)

    raw = score
    score = max(-100.0, min(100.0, raw * cfg.raw_scale))
    values["raw_score"] = raw
    values["scaled_score"] = score

    return LaneResult(name="flow", score=score, evidence=evidence, values=values)
