from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request

from engine.config import load_config
from engine.data import DataLayer

router = APIRouter()


@router.get("/flows/snapshot")
def flows_snapshot(
    request: Request,
    symbols: str = Query("BTC/USDT,ETH/USDT,SOL/USDT"),
) -> dict:
    cfg = load_config()
    data = DataLayer(cfg)
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()][:20]
    rows = []
    for sym in sym_list:
        funding = data.get_funding(sym)
        oi = data.get_oi(sym, "1h")
        current = funding.get("current") or {}
        rate = current.get("fundingRate")
        oi_change = None
        if len(oi) >= 2 and "openInterestValue" in oi.columns:
            prev = float(oi["openInterestValue"].iloc[-2])
            last = float(oi["openInterestValue"].iloc[-1])
            if prev:
                oi_change = (last - prev) / prev
        rows.append(
            {
                "symbol": sym,
                "funding_rate": rate,
                "funding_rate_pct": float(rate) * 100 if rate is not None else None,
                "open_interest_usd": float(oi["openInterestValue"].iloc[-1])
                if len(oi) and "openInterestValue" in oi.columns
                else None,
                "oi_change_1bar": oi_change,
            }
        )
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "symbols": sym_list,
        "rows": rows,
    }
