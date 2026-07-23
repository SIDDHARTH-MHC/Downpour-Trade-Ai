from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query, Request

from api.db import Database

router = APIRouter()


@router.get("/history")
def history(
    request: Request,
    symbol: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
) -> dict:
    db = Database()
    rows = db.list_verdicts(symbol=symbol, limit=limit)
    open_items = db.open_outcomes()
    outcome_map = {item["verdict_id"]: item for item in open_items}
    enriched = []
    for row in rows:
        item = dict(row)
        item["request_id"] = getattr(request.state, "request_id", None)
        enriched.append(item)
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "count": len(enriched),
        "verdicts": enriched,
        "open_outcomes": len(outcome_map),
    }
