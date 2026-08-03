"""Stable hash of engine config for verdict reproducibility."""

from __future__ import annotations

import hashlib
import json

from engine.config import EngineConfig


def config_hash(config: EngineConfig) -> str:
    payload = config.model_dump(mode="json")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]
