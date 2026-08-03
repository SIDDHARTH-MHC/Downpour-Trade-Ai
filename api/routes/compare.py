from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Query, Request

from api.cache import cached_verdict
from api.db import Database
from api.verdict_enrich import enrich_verdict_payload
from engine.analyzer import analyze_symbol
from engine.config import load_config

router = APIRouter()

LANE_NAMES = ("technical", "flow", "structure")


@router.get("/compare")
def compare(
    request: Request,
    a: str = Query("BTC/USDT"),
    b: str = Query("ETH/USDT"),
    tf: str = Query("1h"),
) -> dict:
    cfg = load_config()
    db = Database()
    side: dict[str, dict] = {}

    for sym in (a, b):
        cache_key = f"compare:{sym}:{tf}"

        def load(s=sym) -> dict:
            try:
                verdict = analyze_symbol(s, tf, light=True, config=cfg)
            except Exception as exc:  # noqa: BLE001
                raise HTTPException(status_code=502, detail=f"{s}: {exc}") from exc
            payload = verdict.to_dict()
            payload["data_as_of_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return enrich_verdict_payload(payload, db)

        side[sym] = cached_verdict(cache_key, load)

    def lane_scores(payload: dict) -> dict[str, float]:
        out: dict[str, float] = {}
        for lane in payload.get("lanes") or []:
            if lane.get("name") in LANE_NAMES:
                out[lane["name"]] = lane.get("score", 0)
        return out

    return {
        "app": "Downpour Trade AI",
        "timeframe": tf,
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "a": {
            "symbol": a,
            "action": side[a].get("action"),
            "weighted_score": side[a].get("weighted_score"),
            "confidence": side[a].get("confidence"),
            "regime": side[a].get("regime", {}).get("name"),
            "lanes": lane_scores(side[a]),
            "trust": side[a].get("trust"),
        },
        "b": {
            "symbol": b,
            "action": side[b].get("action"),
            "weighted_score": side[b].get("weighted_score"),
            "confidence": side[b].get("confidence"),
            "regime": side[b].get("regime", {}).get("name"),
            "lanes": lane_scores(side[b]),
            "trust": side[b].get("trust"),
        },
    }
