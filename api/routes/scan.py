from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request

from api.db import Database
from api.scheduler import run_scan

router = APIRouter()


@router.get("/scan")
def scan(
    request: Request,
    tf: str = Query("1h"),
    refresh: bool = Query(False),
) -> dict:
    db = Database()
    if refresh:
        results = run_scan(tf=tf)
    else:
        results = db.latest_scan(tf)
    actionable = [r for r in results if r.get("action") != "NO_TRADE"]
    return {
        "app": "Downpour Trade AI",
        "timeframe": tf,
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "total": len(results),
        "actionable_count": len(actionable),
        "results": results,
        "actionable": actionable,
    }
