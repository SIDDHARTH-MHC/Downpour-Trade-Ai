from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from api.limiter import limiter
from engine.analyzer import analyze_symbol
from engine.config import load_config

router = APIRouter()


@router.get("/analyze/batch")
@limiter.limit("10/minute")
def analyze_batch(
    request: Request,
    symbols: str = Query(..., description="Comma-separated symbols, max 12"),
    tf: str = Query("1h"),
) -> dict:
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]
    if not sym_list:
        raise HTTPException(status_code=400, detail="symbols required")
    if len(sym_list) > 12:
        raise HTTPException(status_code=400, detail="max 12 symbols per batch")

    cfg = load_config()
    results = []
    errors: dict[str, str] = {}
    for sym in sym_list:
        try:
            verdict = analyze_symbol(sym, tf, persist=False, light=True, config=cfg)
            payload = verdict.to_dict()
            payload["data_as_of_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            results.append(payload)
        except Exception as exc:  # noqa: BLE001
            errors[sym] = str(exc)

    return {
        "app": "Downpour Trade AI",
        "timeframe": tf,
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "results": results,
        "errors": errors,
    }
