from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from api.db import Database

router = APIRouter()


class AlertRuleBody(BaseModel):
    id: int | None = None
    name: str = Field(min_length=1, max_length=80)
    enabled: bool = True
    actions: str = "LONG,SHORT"
    min_score: float = 35
    confidence_contains: str = ""
    telegram: bool = True
    webhook_url: str = ""


@router.get("/alerts/rules")
def list_rules(request: Request) -> dict:
    db = Database()
    rules = db.list_alert_rules()
    for rule in rules:
        rule["enabled"] = bool(rule.get("enabled"))
        rule["telegram"] = bool(rule.get("telegram"))
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "rules": rules,
    }


@router.post("/alerts/rules")
def upsert_rule(request: Request, body: AlertRuleBody) -> dict:
    db = Database()
    rule_id = db.save_alert_rule(body.model_dump())
    return {
        "app": "Downpour Trade AI",
        "id": rule_id,
        "request_id": getattr(request.state, "request_id", None),
    }


@router.delete("/alerts/rules/{rule_id}")
def delete_rule(request: Request, rule_id: int) -> dict:
    db = Database()
    db.delete_alert_rule(rule_id)
    return {"app": "Downpour Trade AI", "deleted": rule_id}
