from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request

from api.db import Database
from api.scheduler import refresh_pairs
from engine.data import DataLayer

router = APIRouter()


@router.get("/pairs")
def pairs(
    request: Request,
    limit: int = Query(50, ge=1, le=100),
    refresh: bool = Query(False),
) -> dict:
    db = Database()
    if refresh:
        refresh_pairs()
    stored = db.list_pairs(limit=limit)
    if stored:
        return {
            "app": "Downpour Trade AI",
            "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "request_id": getattr(request.state, "request_id", None),
            "pairs": stored,
        }

    data = DataLayer()
    symbols = data.get_top_volume_pairs(limit)
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "pairs": [{"symbol": s} for s in symbols],
    }
