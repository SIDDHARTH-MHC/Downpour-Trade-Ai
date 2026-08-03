"""Record engine capability matrix snapshots (informational)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from engine.config import load_config
from engine.config_hash import config_hash


def default_capabilities(cfg=None) -> list[str]:
    c = cfg or load_config()
    caps = [
        "technical_orthogonalization_t3",
        "flow_funding_oi",
        "flow_long_short_ratio",
        "structure_sweep",
        "structure_fvg_events",
        "structure_equal_high_low",
        "regime_macro_dxy",
        "session_vwap_evidence",
    ]
    if c.flow.long_short_ratio_enabled:
        caps.append("flow_ls_zscore")
    if c.regime.macro_dxy_risk_off_enabled:
        caps.append("regime_dxy_gate")
    return caps


def record_capability_matrix(
    *,
    engine_release_id: str,
    version_label: str,
    capabilities: list[str] | None = None,
    details: dict[str, Any] | None = None,
) -> str | None:
    from research_platform.config import get_research_settings

    if not get_research_settings().research_db_enabled:
        return None

    from research_platform.db.session import research_session
    from research_platform.models.platform_extras import EngineCapabilityMatrix

    row_id = str(uuid.uuid4())
    caps = capabilities or default_capabilities()
    with research_session() as session:
        if session is None:
            return None
        session.add(
            EngineCapabilityMatrix(
                id=row_id,
                engine_release_id=engine_release_id,
                version_label=version_label,
                capabilities=caps,
                capability_details=details or {"config_hash": config_hash(load_config())},
                recorded_at=datetime.now(timezone.utc),
            )
        )
    return row_id
