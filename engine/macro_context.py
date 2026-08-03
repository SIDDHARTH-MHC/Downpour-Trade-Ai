"""Macro context for regime warnings (Context / Regime — not lane scores)."""

from __future__ import annotations

import json
import urllib.request
from datetime import datetime, timezone


def _fetch_stooq_daily(symbol: str) -> list[tuple[str, float]]:
    """Stooq CSV: Date,Open,High,Low,Close,Volume"""
    url = f"https://stooq.com/q/d/l/?s={symbol}&i=d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DownpourTradeAI/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            text = resp.read().decode()
    except Exception:
        return []
    rows: list[tuple[str, float]] = []
    lines = text.strip().splitlines()
    for line in lines[1:]:
        parts = line.split(",")
        if len(parts) < 5:
            continue
        try:
            rows.append((parts[0], float(parts[4])))
        except ValueError:
            continue
    return rows


def macro_risk_snapshot() -> dict:
    """
    DXY proxy via Stooq (dx.f). Used for regime evidence only — not a lane score.
    """
    from engine.config import load_config

    cfg = load_config().regime
    threshold = cfg.macro_dxy_risk_off_pct
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    rows = _fetch_stooq_daily("dx.f")
    if len(rows) < 2:
        return {
            "updated_at_utc": updated,
            "dxy_24h_pct": None,
            "risk_off": False,
            "risk_off_threshold_pct": threshold,
            "source": "stooq",
        }

    prev_close = rows[-2][1]
    last_close = rows[-1][1]
    if prev_close <= 0:
        pct = None
    else:
        pct = (last_close - prev_close) / prev_close

    risk_off = pct is not None and pct >= threshold
    return {
        "updated_at_utc": updated,
        "dxy_last": last_close,
        "dxy_24h_pct": pct,
        "risk_off": risk_off,
        "risk_off_threshold_pct": threshold,
        "regime_gate_enabled": cfg.macro_dxy_risk_off_enabled,
        "source": "stooq",
        "disclaimer": "Context only — regime weight nudge when macro_dxy_risk_off_enabled.",
    }


def macro_snapshot_json() -> str:
    return json.dumps(macro_risk_snapshot())
