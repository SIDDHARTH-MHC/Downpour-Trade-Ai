from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Query, Request

from api.db import Database

router = APIRouter()


@router.get("/backtest-stats")
def backtest_stats(
    request: Request,
    symbol: str = Query("BTC/USDT"),
    tf: str = Query("1h"),
) -> dict:
    db = Database()
    stats = db.load_calibration()
    if not stats:
        cal_path = Path("data/calibration.json")
        if cal_path.exists():
            stats = json.loads(cal_path.read_text())
    return {
        "app": "Downpour Trade AI",
        "symbol": symbol,
        "timeframe": tf,
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "buckets": stats,
    }
