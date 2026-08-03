from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request

from api.calibration_utils import filter_calibration_buckets
from api.db import Database
from api.trust_utils import trust_payload
from engine.analyzer import analyze_symbol
from engine.config import load_config

router = APIRouter()


@router.get("/trust")
def trust(
    request: Request,
    symbol: str = Query("BTC/USDT"),
    tf: str = Query("1h"),
) -> dict:
    db = Database()
    stats = db.load_calibration()
    buckets = filter_calibration_buckets(stats or {})
    wf = stats.get("walk_forward") if stats else None
    last_cal = db.get_meta("last_calibrated_utc", "never")

    try:
        verdict = analyze_symbol(symbol, tf, config=load_config())
        payload = verdict.to_dict()
    except Exception as exc:  # noqa: BLE001
        payload = {
            "action": "NO_TRADE",
            "weighted_score": 0.0,
            "confidence": "N/A",
        }

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    card = trust_payload(
        action=payload.get("action", "NO_TRADE"),
        weighted_score=float(payload.get("weighted_score", 0)),
        confidence=str(payload.get("confidence", "N/A")),
        buckets=buckets,
        walk_forward=wf,
        data_as_of_utc=payload.get("data_as_of_utc") or payload.get("timestamp") or now,
        last_calibrated_utc=last_cal,
    )
    return {
        "app": "Downpour Trade AI",
        "symbol": symbol,
        "timeframe": tf,
        "request_id": getattr(request.state, "request_id", None),
        "trust": card,
    }
