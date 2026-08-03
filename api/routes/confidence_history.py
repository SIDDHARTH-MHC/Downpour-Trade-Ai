from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Query, Request

from api.db import Database

router = APIRouter()


def _outcome_label(action: str, outcome: str | None) -> str | None:
    if action not in {"LONG", "SHORT"}:
        return None
    if outcome is None:
        return "OPEN"
    if outcome in {"TP1", "TP2", "WIN"}:
        return "WIN"
    if outcome in {"SL", "LOSS", "TIMEOUT"}:
        return "LOSS"
    return outcome


@router.get("/confidence-history")
def confidence_history(
    request: Request,
    symbol: Optional[str] = Query(None),
    limit: int = Query(30, ge=1, le=200),
) -> dict:
    db = Database()
    rows = db.list_verdicts_with_outcomes(symbol=symbol, limit=limit)
    points = []
    for row in reversed(rows):
        if row.get("action") == "NO_TRADE":
            continue
        points.append(
            {
                "timestamp": row.get("timestamp"),
                "symbol": row.get("symbol"),
                "timeframe": row.get("timeframe"),
                "action": row.get("action"),
                "weighted_score": row.get("weighted_score"),
                "confidence": row.get("confidence"),
                "outcome": _outcome_label(row.get("action"), row.get("outcome")),
            }
        )
    return {
        "app": "Downpour Trade AI",
        "symbol": symbol,
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "count": len(points),
        "points": points,
    }
