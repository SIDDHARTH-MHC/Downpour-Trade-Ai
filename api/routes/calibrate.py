from __future__ import annotations

import logging
import threading
from datetime import datetime, timezone

from fastapi import APIRouter, Query, Request

from api.db import Database
from api.scheduler import calibration_status, run_calibration_async, run_calibration_sync

router = APIRouter()
logger = logging.getLogger("downpour.calibrate")


@router.get("/calibrate")
def calibrate_status(request: Request) -> dict:
    status = calibration_status()
    db = Database()
    stats = db.load_calibration()
    return {
        "app": "Downpour Trade AI",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        **status,
        "bucket_count": len(stats),
        "buckets": stats,
    }


@router.post("/calibrate")
def start_calibration(
    request: Request,
    tf: str = Query("1h"),
    months: int = Query(6, ge=1, le=18),
    symbols: str = Query("BTC/USDT,ETH/USDT"),
    sync: bool = Query(False, description="Run synchronously (may timeout on free tier)"),
) -> dict:
    status = calibration_status()
    sym_list = [s.strip() for s in symbols.split(",") if s.strip()]

    if status["running"]:
        return {
            "app": "Downpour Trade AI",
            "status": "calibration_in_progress",
            "message": "Calibration already running. Poll GET /calibrate for status.",
            "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "request_id": getattr(request.state, "request_id", None),
            **status,
        }

    if sync:
        stats = run_calibration_sync(sym_list, tf, months)
        return {
            "app": "Downpour Trade AI",
            "status": "calibration_complete",
            "message": f"Calibration complete for {', '.join(sym_list)}.",
            "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "request_id": getattr(request.state, "request_id", None),
            "bucket_count": len(stats),
            "buckets": stats,
        }

    run_calibration_async(sym_list, tf, months)
    return {
        "app": "Downpour Trade AI",
        "status": "calibration_started",
        "message": f"Calibrating {', '.join(sym_list)} over {months} months. Poll GET /calibrate every 30s.",
        "data_as_of_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "request_id": getattr(request.state, "request_id", None),
        "symbols": sym_list,
        "timeframe": tf,
        "months": months,
    }
