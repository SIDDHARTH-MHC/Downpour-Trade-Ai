from __future__ import annotations

from datetime import datetime, timezone

from api.calibration_utils import filter_calibration_buckets
from api.db import Database
from api.trust_utils import trust_payload
from engine.replay import build_replay_events


def enrich_verdict_payload(payload: dict, db: Database | None = None) -> dict:
    db = db or Database()
    stats = db.load_calibration()
    buckets = filter_calibration_buckets(stats or {})
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    payload.setdefault("data_as_of_utc", now)
    payload["trust"] = trust_payload(
        action=payload.get("action", "NO_TRADE"),
        weighted_score=float(payload.get("weighted_score", 0)),
        confidence=str(payload.get("confidence", "N/A")),
        buckets=buckets,
        walk_forward=stats.get("walk_forward") if stats else None,
        data_as_of_utc=payload["data_as_of_utc"],
        last_calibrated_utc=db.get_meta("last_calibrated_utc", "never"),
    )
    payload["replay_events"] = build_replay_events(payload)
    return payload
