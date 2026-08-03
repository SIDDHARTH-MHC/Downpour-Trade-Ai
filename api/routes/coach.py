from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from api.coach import coach_reply
from api.limiter import limiter

router = APIRouter()


class CoachBody(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    symbol: str | None = None
    action: str | None = None


@router.post("/coach/chat")
@limiter.limit("30/minute")
def coach_chat(request: Request, body: CoachBody) -> dict:
    ctx = {"symbol": body.symbol, "action": body.action}
    reply = coach_reply(body.message, ctx)
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "topic": reply["topic"],
        "markdown": reply["markdown"],
        "disclaimer": "Educational coach only — not trading advice. Does not change engine output.",
    }
