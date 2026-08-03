from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, Field

from api.db import Database

router = APIRouter()


class JournalBody(BaseModel):
    id: int | None = None
    symbol: str | None = None
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=20000)
    tags: str = ""


@router.get("/journal")
def list_journal(request: Request, limit: int = Query(50, ge=1, le=200)) -> dict:
    db = Database()
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "entries": db.list_journal(limit=limit),
    }


@router.post("/journal")
def save_journal(request: Request, body: JournalBody) -> dict:
    db = Database()
    entry_id = db.save_journal(body.model_dump())
    return {
        "app": "Downpour Trade AI",
        "id": entry_id,
        "request_id": getattr(request.state, "request_id", None),
    }


@router.delete("/journal/{entry_id}")
def delete_journal(request: Request, entry_id: int) -> dict:
    Database().delete_journal(entry_id)
    return {"app": "Downpour Trade AI", "deleted": entry_id}
