from __future__ import annotations

import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from api.db import Database
from api.engine_health import probe_health

router = APIRouter()


@router.get("/status")
def engine_status(request: Request) -> dict:
    health = probe_health()
    db = Database()
    raw = db.get_meta("last_scan_report", "")
    scan_report = json.loads(raw) if raw else None
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        **health,
        "last_scan_report": scan_report,
    }
