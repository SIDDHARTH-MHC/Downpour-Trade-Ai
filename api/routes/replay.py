from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from api.db import Database
from engine.lifecycle import lifecycle_state
from engine.replay import build_replay_events

router = APIRouter()


@router.get("/replay")
def replay(
    request: Request,
    verdict_id: int | None = Query(None),
    symbol: str | None = Query(None),
    tf: str = Query("1h"),
) -> dict:
    db = Database()
    payload = None
    if verdict_id is not None:
        payload = db.get_verdict_by_id(verdict_id)
    elif symbol:
        rows = db.list_verdicts(symbol=symbol, limit=1)
        payload = rows[0] if rows else None
        if payload:
            payload["verdict_id"] = None

    if not payload:
        raise HTTPException(status_code=404, detail="verdict not found")

    events = payload.get("replay_events") or build_replay_events(payload)
    life = lifecycle_state(payload, payload.get("outcome"))
    return {
        "app": "Downpour Trade AI",
        "verdict_id": payload.get("verdict_id"),
        "symbol": payload.get("symbol"),
        "timeframe": payload.get("timeframe", tf),
        "action": payload.get("action"),
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "events": events,
        "lifecycle": life,
    }
