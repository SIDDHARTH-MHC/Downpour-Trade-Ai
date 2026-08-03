from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from api.limiter import limiter
from api.cache import cached_verdict
from api.db import Database
from api.verdict_enrich import enrich_verdict_payload
from engine.analyzer import analyze_symbol
from engine.config import load_config

router = APIRouter()


@router.get("/analyze")
@limiter.limit("30/minute")
def analyze(
    request: Request,
    symbol: str = Query("BTC/USDT"),
    tf: str = Query("1h"),
    patient: bool = Query(False),
    equity: float = Query(10_000.0),
    persist: bool = Query(True),
) -> dict:
    cache_key = f"{symbol}:{tf}:{patient}:{equity}"

    def load() -> dict:
        try:
            verdict = analyze_symbol(symbol, tf, patient=patient, equity_usd=equity, config=load_config())
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        payload = verdict.to_dict()
        payload["data_as_of_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        payload["request_id"] = getattr(request.state, "request_id", None)
        db = Database()
        enrich_verdict_payload(payload, db)
        if persist:
            db.save_verdict(payload)
        return payload

    return cached_verdict(cache_key, load)
