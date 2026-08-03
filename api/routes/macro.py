from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request

from engine.config import load_config
from engine.data import DataLayer
from engine.macro_context import macro_risk_snapshot

router = APIRouter()

_macro_cache: dict | None = None
_macro_cache_at: float = 0.0


@router.get("/macro/snapshot")
def macro_snapshot(request: Request) -> dict:
    global _macro_cache, _macro_cache_at
    import time

    now = time.time()
    if _macro_cache and now - _macro_cache_at < 300:
        snap = dict(_macro_cache)
    else:
        data = DataLayer(load_config())
        snap = data.get_macro_snapshot()
        if "error" not in snap:
            _macro_cache = snap
            _macro_cache_at = now

    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "macro": snap,
    }


@router.get("/macro/risk")
def macro_risk(request: Request) -> dict:
    risk = macro_risk_snapshot()
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "risk": risk,
    }
