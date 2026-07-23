from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request

from api.cache import cache_stats
from api.db import Database

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict:
    db = Database()
    return {
        "status": "ok",
        "app": "Downpour Trade AI",
        "last_scan_utc": db.get_meta("last_scan_utc", "never"),
        "data_freshness": cache_stats(),
        "request_id": getattr(request.state, "request_id", None),
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    }
