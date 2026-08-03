from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from api.db import Database
from api.settings import get_settings

router = APIRouter()


class IntegrationsBody(BaseModel):
    discord_webhook_url: str = ""
    slack_webhook_url: str = ""


@router.get("/integrations")
def get_integrations(request: Request) -> dict:
    db = Database()
    settings = get_settings()
    stored = db.get_integration_urls()
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "discord_webhook_url": stored.get("discord_webhook_url") or settings.discord_webhook_url,
        "slack_webhook_url": stored.get("slack_webhook_url") or settings.slack_webhook_url,
        "telegram_configured": bool(settings.telegram_bot_token and settings.telegram_chat_id),
        "note": "Discord/Slack receive actionable scan alerts when URLs are set.",
    }


@router.post("/integrations")
def save_integrations(request: Request, body: IntegrationsBody) -> dict:
    db = Database()
    db.set_integration_urls(body.discord_webhook_url, body.slack_webhook_url)
    return {"app": "Downpour Trade AI", "saved": True}
