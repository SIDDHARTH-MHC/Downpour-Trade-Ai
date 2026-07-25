from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from api.calibration_utils import filter_calibration_buckets, is_bucket_stats
from api.settings import get_settings


def _utcnow() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self, url: str | None = None) -> None:
        settings = get_settings()
        self.url = url or settings.database_url
        if self.url.startswith("sqlite:///"):
            path = self.url.replace("sqlite:///", "")
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            self.path = path
        else:
            self.path = "./data/downpour.db"

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def init(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS verdicts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    tf TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    weighted_score REAL NOT NULL,
                    confidence TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS outcomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    verdict_id INTEGER NOT NULL,
                    outcome TEXT,
                    resolved_at TEXT,
                    FOREIGN KEY (verdict_id) REFERENCES verdicts(id)
                );
                CREATE TABLE IF NOT EXISTS calibration (
                    bucket TEXT PRIMARY KEY,
                    stats_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS scan_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tf TEXT NOT NULL,
                    results_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS pairs (
                    symbol TEXT PRIMARY KEY,
                    volume REAL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                """
            )

    def save_verdict(self, payload: dict[str, Any]) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO verdicts (symbol, tf, timestamp, action, weighted_score, confidence, payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    payload["symbol"],
                    payload["timeframe"],
                    payload["timestamp"],
                    payload["action"],
                    payload["weighted_score"],
                    payload["confidence"],
                    json.dumps(payload),
                    _utcnow(),
                ),
            )
            verdict_id = int(cur.lastrowid)
            if payload.get("action") in {"LONG", "SHORT"}:
                conn.execute(
                    "INSERT INTO outcomes (verdict_id, outcome, resolved_at) VALUES (?, NULL, NULL)",
                    (verdict_id,),
                )
            return verdict_id

    def list_verdicts(self, symbol: str | None = None, limit: int = 50) -> list[dict]:
        query = "SELECT payload FROM verdicts"
        params: list[Any] = []
        if symbol:
            query += " WHERE symbol = ?"
            params.append(symbol)
        query += " ORDER BY id DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [json.loads(row["payload"]) for row in rows]

    def save_scan(self, tf: str, results: list[dict]) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO scan_runs (tf, results_json, created_at) VALUES (?, ?, ?)",
                (tf, json.dumps(results), _utcnow()),
            )

    def latest_scan(self, tf: str) -> list[dict]:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT results_json FROM scan_runs WHERE tf = ? ORDER BY id DESC LIMIT 1",
                (tf,),
            ).fetchone()
        return json.loads(row["results_json"]) if row else []

    def save_pairs(self, pairs: list[tuple[str, float]]) -> None:
        with self.connect() as conn:
            for symbol, volume in pairs:
                conn.execute(
                    "INSERT OR REPLACE INTO pairs (symbol, volume, updated_at) VALUES (?, ?, ?)",
                    (symbol, volume, _utcnow()),
                )

    def list_pairs(self, limit: int = 50) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT symbol, volume, updated_at FROM pairs ORDER BY volume DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_calibration(self, stats: dict) -> None:
        buckets = filter_calibration_buckets(stats)
        walk_forward = stats.get("walk_forward")
        with self.connect() as conn:
            for bucket, data in buckets.items():
                conn.execute(
                    "INSERT OR REPLACE INTO calibration (bucket, stats_json, updated_at) VALUES (?, ?, ?)",
                    (bucket, json.dumps(data), _utcnow()),
                )
            conn.execute("DELETE FROM calibration WHERE bucket = ?", ("walk_forward",))
            if isinstance(walk_forward, list):
                conn.execute(
                    "INSERT OR REPLACE INTO calibration (bucket, stats_json, updated_at) VALUES (?, ?, ?)",
                    ("_walk_forward", json.dumps(walk_forward), _utcnow()),
                )

    def load_calibration(self) -> dict:
        with self.connect() as conn:
            rows = conn.execute("SELECT bucket, stats_json FROM calibration").fetchall()
        result: dict = {}
        for row in rows:
            if row["bucket"] == "_walk_forward":
                result["walk_forward"] = json.loads(row["stats_json"])
                continue
            if row["bucket"] == "walk_forward":
                continue
            value = json.loads(row["stats_json"])
            if is_bucket_stats(value):
                result[row["bucket"]] = value
        return result

    def set_meta(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO meta (key, value) VALUES (?, ?)",
                (key, value),
            )

    def get_meta(self, key: str, default: str = "") -> str:
        with self.connect() as conn:
            row = conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def open_outcomes(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT o.id, o.verdict_id, v.payload
                FROM outcomes o
                JOIN verdicts v ON v.id = o.verdict_id
                WHERE o.outcome IS NULL
                """
            ).fetchall()
        items = []
        for row in rows:
            payload = json.loads(row["payload"])
            items.append({"outcome_id": row["id"], "verdict_id": row["verdict_id"], "payload": payload})
        return items

    def resolve_outcome(self, outcome_id: int, outcome: str) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE outcomes SET outcome = ?, resolved_at = ? WHERE id = ?",
                (outcome, _utcnow(), outcome_id),
            )
