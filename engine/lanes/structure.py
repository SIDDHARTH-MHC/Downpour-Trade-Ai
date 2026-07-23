"""Lane 3 — Structure: S/R + order-book walls."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from engine.config import EngineConfig, load_config
from engine.data import DataLayer
from engine.indicators import atr_wilder
from engine.models import LaneResult


@dataclass
class SRLevel:
    price: float
    kind: str  # support | resistance
    touches: int


@dataclass
class Wall:
    price: float
    side: str
    notional_usd: float


def detect_swings(df: pd.DataFrame, n: int = 5) -> tuple[list[float], list[float]]:
    highs, lows = [], []
    for i in range(n, len(df) - n):
        window_high = df["high"].iloc[i - n : i + n + 1]
        window_low = df["low"].iloc[i - n : i + n + 1]
        if df["high"].iloc[i] == window_high.max():
            highs.append(float(df["high"].iloc[i]))
        if df["low"].iloc[i] == window_low.min():
            lows.append(float(df["low"].iloc[i]))
    return highs, lows


def cluster_levels(points: list[float], atr: float, factor: float) -> list[tuple[float, int]]:
    if not points:
        return []
    points = sorted(points)
    clusters: list[list[float]] = [[points[0]]]
    threshold = atr * factor
    for p in points[1:]:
        if abs(p - clusters[-1][-1]) <= threshold:
            clusters[-1].append(p)
        else:
            clusters.append([p])
    return [(float(np.mean(c)), len(c)) for c in clusters]


def nearest_levels(price: float, supports: list[SRLevel], resistances: list[SRLevel], max_levels: int) -> tuple[list[SRLevel], list[SRLevel]]:
    all_levels = supports + resistances
    all_levels.sort(key=lambda lv: abs(lv.price - price))
    nearest = all_levels[:max_levels]
    sup = [lv for lv in nearest if lv.kind == "support"]
    res = [lv for lv in nearest if lv.kind == "resistance"]
    return sup, res


def detect_walls(book: dict, price: float, symbol: str, cfg) -> list[Wall]:
    # Order-book walls can be spoofed and pulled; capped influence in scoring.
    min_notional = cfg.wall_min_notional_btc_eth if DataLayer.is_major(symbol) else cfg.wall_min_notional_alt
    bucket_pct = cfg.wall_bucket_pct
    buckets: dict[tuple[str, float], float] = {}

    for side, levels in [("bid", book.get("bids", [])), ("ask", book.get("asks", []))]:
        for lvl_price, amount in levels:
            bucket = round(float(lvl_price) / (price * bucket_pct)) * (price * bucket_pct)
            notional = float(lvl_price) * float(amount)
            buckets[(side, bucket)] = buckets.get((side, bucket), 0) + notional

    if not buckets:
        return []

    notionals = list(buckets.values())
    median = float(np.median(notionals))
    walls: list[Wall] = []
    for (side, bucket_price), notional in buckets.items():
        if notional > cfg.wall_median_multiplier * median and notional >= min_notional:
            walls.append(Wall(price=float(bucket_price), side=side, notional_usd=notional))
    walls.sort(key=lambda w: abs(w.price - price))
    return walls


def analyze_structure(
    df: pd.DataFrame,
    book: dict | None,
    symbol: str,
    config: EngineConfig | None = None,
) -> LaneResult:
    cfg = (config or load_config()).structure
    price = float(df["close"].iloc[-1])
    atr = float(atr_wilder(df["high"], df["low"], df["close"], 14).iloc[-1])
    values: dict[str, float] = {"price": price, "atr14": atr}
    evidence: list[str] = []
    score = 0.0
    wall_contribution = 0.0
    no_edge = False

    swing_highs, swing_lows = detect_swings(df, cfg.swing_fractal)
    sup_clusters = cluster_levels(swing_lows, atr, cfg.cluster_atr_factor)
    res_clusters = cluster_levels(swing_highs, atr, cfg.cluster_atr_factor)

    supports = [SRLevel(price=p, kind="support", touches=t) for p, t in sup_clusters]
    resistances = [SRLevel(price=p, kind="resistance", touches=t) for p, t in res_clusters]
    near_sup, near_res = nearest_levels(price, supports, resistances, cfg.max_levels)

    nearest_support = min(near_sup, key=lambda lv: price - lv.price, default=None) if near_sup else None
    nearest_resistance = min(near_res, key=lambda lv: lv.price - price, default=None) if near_res else None

    dist_support = (price - nearest_support.price) / atr if nearest_support else float("inf")
    dist_resistance = (nearest_resistance.price - price) / atr if nearest_resistance else float("inf")

    walls_preview: list[Wall] = detect_walls(book, price, symbol, cfg) if book else []
    strong_bid_wall = any(
        w.side == "bid" and (price - w.price) / atr <= cfg.support_near_atr for w in walls_preview
    )
    strong_ask_wall = any(
        w.side == "ask" and (w.price - price) / atr <= cfg.resistance_near_atr for w in walls_preview
    )

    near_support = dist_support <= cfg.support_near_atr or strong_bid_wall
    if near_support:
        if nearest_support and (nearest_support.touches >= cfg.min_touch_breakout or strong_bid_wall):
            score += cfg.support_score
            if nearest_support.touches >= 3:
                reason = f"touches={nearest_support.touches}"
                lvl = nearest_support.price
            else:
                reason = "bid wall"
                lvl = nearest_support.price if nearest_support else walls_preview[0].price
            dist = dist_support if nearest_support else (price - lvl) / atr
            evidence.append(
                f"support {lvl:.2f} at {dist:.1f} ATR, {reason} (+{cfg.support_score:.0f})"
            )
        elif strong_bid_wall:
            wall = next(w for w in walls_preview if w.side == "bid")
            dist = (price - wall.price) / atr
            score += cfg.support_score
            evidence.append(
                f"bid wall ${wall.notional_usd/1e6:.1f}M @ {wall.price:.0f}, {dist:.1f} ATR (+{cfg.support_score:.0f})"
            )

    near_resistance = dist_resistance <= cfg.resistance_near_atr or strong_ask_wall
    if near_resistance:
        if nearest_resistance and (nearest_resistance.touches >= cfg.min_touch_breakout or strong_ask_wall):
            score += cfg.resistance_score
            if nearest_resistance.touches >= 3:
                reason = f"touches={nearest_resistance.touches}"
            else:
                reason = "ask wall"
            evidence.append(
                f"resistance {nearest_resistance.price:.2f} at {dist_resistance:.1f} ATR, {reason} ({cfg.resistance_score:.0f})"
            )
        elif strong_ask_wall:
            wall = next(w for w in walls_preview if w.side == "ask")
            dist = (wall.price - price) / atr
            score += cfg.resistance_score
            evidence.append(
                f"ask wall ${wall.notional_usd/1e6:.1f}M @ {wall.price:.0f}, {dist:.1f} ATR ({cfg.resistance_score:.0f})"
            )

    if dist_support > cfg.range_no_edge_atr and dist_resistance > cfg.range_no_edge_atr and not strong_bid_wall and not strong_ask_wall:
        no_edge = True
        evidence.append(f"price mid-range ({dist_support:.1f}/{dist_resistance:.1f} ATR from S/R) → no_edge")

    avg_vol = float(df["volume"].iloc[-21:-1].mean()) if len(df) > 21 else float(df["volume"].mean())
    last_vol = float(df["volume"].iloc[-1])
    if nearest_resistance and price > nearest_resistance.price and nearest_resistance.touches >= cfg.min_touch_breakout:
        if last_vol > avg_vol:
            score += cfg.breakout_score
            evidence.append(f"breakout above {nearest_resistance.price:.2f} on vol {last_vol:.0f}>{avg_vol:.0f} (+{cfg.breakout_score:.0f})")

    if nearest_support and price < nearest_support.price and nearest_support.touches >= cfg.min_touch_breakout:
        if last_vol > avg_vol:
            score += cfg.breakdown_score
            evidence.append(f"breakdown below {nearest_support.price:.2f} on vol ({cfg.breakdown_score:.0f})")

    walls: list[Wall] = walls_preview
    if book and walls:
        bid_near = sum(w.notional_usd for w in walls if w.side == "bid" and abs(w.price - price) / price <= 0.02)
        ask_near = sum(w.notional_usd for w in walls if w.side == "ask" and abs(w.price - price) / price <= 0.02)
        if bid_near and ask_near:
            ratio = bid_near / ask_near
            values["bid_ask_wall_ratio"] = ratio
            if ratio > cfg.bid_ask_ratio_high:
                wall_contribution += cfg.bid_ask_ratio_bull
                evidence.append(f"bid/ask wall ratio={ratio:.2f} (+{cfg.bid_ask_ratio_bull:.0f})")
            elif ratio < cfg.bid_ask_ratio_low:
                wall_contribution += cfg.bid_ask_ratio_bear
                evidence.append(f"bid/ask wall ratio={ratio:.2f} ({cfg.bid_ask_ratio_bear:.0f})")

        min_notional = cfg.wall_min_notional_btc_eth if DataLayer.is_major(symbol) else cfg.wall_min_notional_alt
        for w in walls[:3]:
            if w.side == "bid" and (price - w.price) / atr <= cfg.support_near_atr and w.notional_usd >= min_notional / 2:
                wall_contribution += min(cfg.support_score / 2, cfg.wall_max_contribution - abs(wall_contribution))
                evidence.append(f"bid wall ${w.notional_usd/1e6:.1f}M @ {w.price:.0f}")
            if w.side == "ask" and (w.price - price) / atr <= cfg.resistance_near_atr:
                wall_contribution -= min(abs(cfg.resistance_score) / 2, cfg.wall_max_contribution - abs(wall_contribution))
                evidence.append(f"ask wall ${w.notional_usd/1e6:.1f}M @ {w.price:.0f} (+/- capped)")

    wall_contribution = max(-cfg.wall_max_contribution, min(cfg.wall_max_contribution, wall_contribution))
    score += wall_contribution
    score = max(-100.0, min(100.0, score))

    if not evidence:
        evidence.append(
            f"no structural edge: support {dist_support:.1f} ATR below, resistance {dist_resistance:.1f} ATR above (0)"
        )

    if nearest_support:
        values["nearest_support"] = nearest_support.price
    if nearest_resistance:
        values["nearest_resistance"] = nearest_resistance.price

    return LaneResult(name="structure", score=score, evidence=evidence, values=values, no_edge=no_edge)
