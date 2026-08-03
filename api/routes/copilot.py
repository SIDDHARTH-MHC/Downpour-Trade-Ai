from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from api.cache import cached_verdict
from api.copilot import explain_markdown
from api.db import Database
from api.limiter import limiter
from api.verdict_enrich import enrich_verdict_payload
from engine.analyzer import analyze_symbol
from engine.config import load_config

router = APIRouter()


@router.post("/copilot/explain")
@limiter.limit("20/minute")
def copilot_explain(
    request: Request,
    symbol: str = Query("BTC/USDT"),
    tf: str = Query("1h"),
    verdict_id: int | None = Query(None),
) -> dict:
    db = Database()
    if verdict_id is not None:
        payload = db.get_verdict_by_id(verdict_id)
        if not payload:
            raise HTTPException(status_code=404, detail="verdict not found")
        enrich_verdict_payload(payload, db)
    else:
        cache_key = f"copilot:{symbol}:{tf}"

        def load() -> dict:
            verdict = analyze_symbol(symbol, tf, persist=False, config=load_config())
            payload = verdict.to_dict()
            payload["data_as_of_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return enrich_verdict_payload(payload, db)

        payload = cached_verdict(cache_key, load)

    markdown = explain_markdown(payload)
    return {
        "app": "Downpour Trade AI",
        "symbol": payload.get("symbol", symbol),
        "timeframe": payload.get("timeframe", tf),
        "action": payload.get("action"),
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "markdown": markdown,
        "disclaimer": "Explain-only — cites engine JSON. Not trading advice.",
    }
