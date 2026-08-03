from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request

from api.db import Database
from engine.config import load_config
from engine.portfolio_analytics import portfolio_analytics

router = APIRouter()


@router.get("/portfolio/analytics")
def portfolio_route(
    request: Request,
    equity: float = Query(10_000.0, ge=100, le=10_000_000),
) -> dict:
    db = Database()
    open_items = db.open_outcomes()
    stats = portfolio_analytics(open_items, equity_usd=equity, config=load_config())
    cfg = load_config().risk
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "config_risk": {
            "account_risk_pct": cfg.account_risk_pct,
            "min_reward_risk": cfg.min_reward_risk,
            "default_equity_usd": cfg.default_equity_usd,
        },
        **stats,
    }
