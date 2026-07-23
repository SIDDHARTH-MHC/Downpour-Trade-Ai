from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request

from api.db import Database
from api.scheduler import run_scan_async, scan_status

router = APIRouter()


@router.get("/scan")
def scan(
    request: Request,
    tf: str = Query("1h"),
    refresh: bool = Query(False),
    limit: int = Query(8, ge=1, le=20),
) -> dict:
    db = Database()
    status = scan_status()

    if refresh:
        if status["running"]:
            return {
                "app": "Downpour Trade AI",
                "status": "scan_in_progress",
                "timeframe": tf,
                "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                "request_id": getattr(request.state, "request_id", None),
                "message": "Scan already running. Poll /scan in 1-2 minutes.",
                "last_scan_utc": status["last_scan_utc"],
                "total": 0,
                "actionable_count": 0,
                "results": db.latest_scan(tf),
                "actionable": [],
            }

        run_scan_async(tf=tf, limit=limit)
        return {
            "app": "Downpour Trade AI",
            "status": "scan_started",
            "timeframe": tf,
            "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "request_id": getattr(request.state, "request_id", None),
            "message": f"Scanning top {limit} pairs in background. Poll /scan?tf={tf} in 1-2 minutes.",
            "last_scan_utc": status["last_scan_utc"],
            "total": 0,
            "actionable_count": 0,
            "results": db.latest_scan(tf),
            "actionable": [],
        }

    results = db.latest_scan(tf)
    actionable = [r for r in results if r.get("action") != "NO_TRADE"]
    return {
        "app": "Downpour Trade AI",
        "status": "ok",
        "timeframe": tf,
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "last_scan_utc": status["last_scan_utc"],
        "scan_running": status["running"],
        "total": len(results),
        "actionable_count": len(actionable),
        "results": results,
        "actionable": actionable,
    }
