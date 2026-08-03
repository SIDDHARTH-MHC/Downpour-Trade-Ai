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
                CREATE TABLE IF NOT EXISTS alert_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    actions TEXT NOT NULL DEFAULT 'LONG,SHORT',
                    min_score REAL NOT NULL DEFAULT 35,
                    confidence_contains TEXT NOT NULL DEFAULT '',
                    telegram INTEGER NOT NULL DEFAULT 1,
                    webhook_url TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    title TEXT NOT NULL,
                    body TEXT NOT NULL,
                    tags TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
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

    def list_verdicts_with_outcomes(self, symbol: str | None = None, limit: int = 50) -> list[dict]:
        query = """
            SELECT v.id, v.payload, o.outcome, o.resolved_at
            FROM verdicts v
            LEFT JOIN outcomes o ON o.verdict_id = v.id
        """
        params: list[Any] = []
        if symbol:
            query += " WHERE v.symbol = ?"
            params.append(symbol)
        query += " ORDER BY v.id DESC LIMIT ?"
        params.append(limit)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        items = []
        for row in rows:
            payload = json.loads(row["payload"])
            payload["verdict_id"] = row["id"]
            payload["outcome"] = row["outcome"]
            payload["outcome_resolved_at"] = row["resolved_at"]
            items.append(payload)
        return items

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

    def list_alert_rules(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, name, enabled, actions, min_score, confidence_contains, telegram, webhook_url, created_at FROM alert_rules ORDER BY id"
            ).fetchall()
        return [dict(row) for row in rows]

    def save_alert_rule(self, rule: dict) -> int:
        with self.connect() as conn:
            if rule.get("id"):
                conn.execute(
                    """
                    UPDATE alert_rules SET name=?, enabled=?, actions=?, min_score=?, confidence_contains=?, telegram=?, webhook_url=?
                    WHERE id=?
                    """,
                    (
                        rule["name"],
                        1 if rule.get("enabled", True) else 0,
                        rule.get("actions", "LONG,SHORT"),
                        float(rule.get("min_score", 35)),
                        rule.get("confidence_contains", ""),
                        1 if rule.get("telegram", True) else 0,
                        rule.get("webhook_url", ""),
                        rule["id"],
                    ),
                )
                return int(rule["id"])
            cur = conn.execute(
                """
                INSERT INTO alert_rules (name, enabled, actions, min_score, confidence_contains, telegram, webhook_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rule["name"],
                    1 if rule.get("enabled", True) else 0,
                    rule.get("actions", "LONG,SHORT"),
                    float(rule.get("min_score", 35)),
                    rule.get("confidence_contains", ""),
                    1 if rule.get("telegram", True) else 0,
                    rule.get("webhook_url", ""),
                    _utcnow(),
                ),
            )
            return int(cur.lastrowid)

    def delete_alert_rule(self, rule_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))

    def list_journal(self, limit: int = 50) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, symbol, title, body, tags, created_at, updated_at FROM journal_entries ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def save_journal(self, entry: dict) -> int:
        with self.connect() as conn:
            if entry.get("id"):
                conn.execute(
                    """
                    UPDATE journal_entries SET symbol=?, title=?, body=?, tags=?, updated_at=? WHERE id=?
                    """,
                    (
                        entry.get("symbol") or "",
                        entry["title"],
                        entry["body"],
                        entry.get("tags") or "",
                        _utcnow(),
                        entry["id"],
                    ),
                )
                return int(entry["id"])
            cur = conn.execute(
                """
                INSERT INTO journal_entries (symbol, title, body, tags, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.get("symbol") or "",
                    entry["title"],
                    entry["body"],
                    entry.get("tags") or "",
                    _utcnow(),
                    _utcnow(),
                ),
            )
            return int(cur.lastrowid)

    def delete_journal(self, entry_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM journal_entries WHERE id = ?", (entry_id,))

    def get_integration_urls(self) -> dict[str, str]:
        return {
            "discord_webhook_url": self.get_meta("discord_webhook_url", ""),
            "slack_webhook_url": self.get_meta("slack_webhook_url", ""),
        }

    def set_integration_urls(self, discord: str, slack: str) -> None:
        self.set_meta("discord_webhook_url", discord.strip())
        self.set_meta("slack_webhook_url", slack.strip())

    def get_verdict_by_id(self, verdict_id: int) -> dict | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT v.payload, o.outcome
                FROM verdicts v
                LEFT JOIN outcomes o ON o.verdict_id = v.id
                WHERE v.id = ?
                """,
                (verdict_id,),
            ).fetchone()
        if not row:
            return None
        payload = json.loads(row["payload"])
        payload["verdict_id"] = verdict_id
        payload["outcome"] = row["outcome"]
        return payload

