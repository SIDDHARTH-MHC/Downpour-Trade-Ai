from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from api.context_fetch import fetch_etf_context, fetch_news
from api.db import Database
from engine.correlation import correlation_matrix
from engine.liquidity_snapshot import liquidity_snapshot
from engine.scenario import simulate_shock

router = APIRouter()


@router.get("/context/news")
def context_news(request: Request, symbol: str = Query("BTC/USDT")) -> dict:
    news = fetch_news(symbol)
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        **news,
    }


@router.get("/context/etf")
def context_etf(request: Request) -> dict:
    etf = fetch_etf_context()
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "etf": etf,
    }


@router.get("/structure/liquidity")
def structure_liquidity(request: Request, symbol: str = Query("BTC/USDT")) -> dict:
    try:
        snap = liquidity_snapshot(symbol)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        **snap,
    }


@router.get("/correlation/matrix")
def correlation_route(
    request: Request,
    symbols: str = Query("BTC/USDT,ETH/USDT,SOL/USDT"),
    tf: str = Query("1h"),
) -> dict:
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()][:20]
    matrix = correlation_matrix(sym_list, tf=tf)
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        **matrix,
    }


class ScenarioBody(BaseModel):
    shock_pct: float = Field(-0.05, description="e.g. -0.05 for -5%")
    shock_asset: str = "BTC"
    tf: str = "1h"


@router.post("/scenarios/run")
def scenarios_run(request: Request, body: ScenarioBody) -> dict:
    db = Database()
    open_items = db.open_outcomes()
    positions = []
    for item in open_items:
        p = dict(item.get("payload") or {})
        p["verdict_id"] = item.get("verdict_id")
        positions.append(p)
    result = simulate_shock(
        positions,
        shock_asset=body.shock_asset,
        shock_pct=body.shock_pct,
        tf=body.tf,
    )
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "open_positions": len(positions),
        **result,
    }
