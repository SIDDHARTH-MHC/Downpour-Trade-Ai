"""Research Feature Store — cache/acceleration only (Phase 7)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from research_platform.hashes import feature_set_id

CATALOG_VERSION = "2026-08-04"


class FeatureStore:
    """
    Registers materialized feature sets. Raw MDS remains canonical.

    Does not serve live /analyze.
    """

    def register_entry(
        self,
        *,
        engine_git_sha: str,
        config_hash: str,
        feature_manifest_hash: str,
        dataset_version_id: str | None = None,
        storage_uri: str | None = None,
        build_policy: str = "cache",
    ) -> str:
        from research_platform.db.session import research_session
        from research_platform.models.platform_extras import FeatureStoreEntry

        fsid = feature_set_id(
            engine_git_sha,
            config_hash,
            feature_manifest_hash,
            CATALOG_VERSION,
            dataset_version_id,
        )
        if not self._enabled():
            return fsid

        with research_session() as session:
            if session is None:
                return fsid
            existing = session.get(FeatureStoreEntry, fsid)
            if existing:
                return fsid
            session.add(
                FeatureStoreEntry(
                    feature_set_id=fsid,
                    engine_git_sha=engine_git_sha,
                    config_hash=config_hash,
                    feature_manifest_hash=feature_manifest_hash,
                    catalog_version=CATALOG_VERSION,
                    dataset_version_id=dataset_version_id,
                    storage_uri=storage_uri,
                    build_policy=build_policy,
                    created_at=datetime.now(timezone.utc),
                )
            )
        return fsid

    def get_entry(self, feature_set_id_value: str) -> dict[str, Any] | None:
        from research_platform.db.session import research_session
        from research_platform.models.platform_extras import FeatureStoreEntry

        if not self._enabled():
            return None
        with research_session() as session:
            if session is None:
                return None
            row = session.get(FeatureStoreEntry, feature_set_id_value)
            if not row:
                return None
            return {
                "feature_set_id": row.feature_set_id,
                "engine_git_sha": row.engine_git_sha,
                "config_hash": row.config_hash,
                "storage_uri": row.storage_uri,
                "build_policy": row.build_policy,
            }

    @staticmethod
    def _enabled() -> bool:
        from research_platform.config import get_research_settings

        return get_research_settings().research_db_enabled
