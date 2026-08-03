"""Deterministic hashes for research reproducibility (MDS v3)."""

from __future__ import annotations

import hashlib
import json
import subprocess
from typing import Any


def sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sha256_hex_trunc(payload: str, n: int = 16) -> str:
    return sha256_hex(payload)[:n]


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def universe_hash(universe: dict[str, Any]) -> str:
    return sha256_hex(canonical_json(universe))


def dataset_hash(manifest: dict[str, Any]) -> str:
    return sha256_hex(canonical_json(manifest))


def feature_manifest_hash(manifest: dict[str, Any]) -> str:
    return sha256_hex(canonical_json(manifest))


def feature_set_id(
    engine_git_sha: str,
    config_hash: str,
    feature_manifest_hash: str,
    catalog_version: str,
    dataset_version_id: str | None = None,
) -> str:
    body = {
        "engine_git_sha": engine_git_sha,
        "config_hash": config_hash,
        "feature_manifest_hash": feature_manifest_hash,
        "catalog_version": catalog_version,
        "dataset_version_id": dataset_version_id,
    }
    return sha256_hex_trunc(canonical_json(body), 32)


def git_head_sha(default: str = "unknown") -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or default
    except Exception:
        return default


DEFAULT_FEATURE_MANIFEST: dict[str, Any] = {
    "structure_degraded": True,
    "order_book": False,
    "taker_trades": False,
    "long_short_ratio": True,
    "funding_history": True,
    "oi_history": True,
    "macro_dxy": True,
    "notes": "Default backtest fidelity; see docs/BACKTEST_FIDELITY.md",
}
