"""Experiment registry and reproducibility bundles (Phase 8)."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engine.config import load_config
from engine.config_hash import config_hash as engine_config_hash
from research_platform.hashes import (
    DEFAULT_FEATURE_MANIFEST,
    dataset_hash,
    feature_manifest_hash,
    git_head_sha,
    universe_hash,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ExperimentRegistry:
    ARTIFACT_ROOT = Path("research/artifacts")

    def create_run_bundle(
        self,
        *,
        experiment_code: str,
        variant: str,
        run_kind: str,
        symbols: list[str],
        timeframe: str,
        months: int,
        metrics: dict[str, Any],
        universe_snapshot: dict[str, Any] | None = None,
        dataset_version_id: str | None = None,
    ) -> dict[str, Any]:
        cfg = load_config()
        cfg_h = engine_config_hash(cfg)
        fm = dict(DEFAULT_FEATURE_MANIFEST)
        fm_hash = feature_manifest_hash(fm)
        uni = universe_snapshot or {"symbols": symbols, "tier": "T1"}
        u_hash = universe_hash(uni)
        manifest = {
            "mds_schema_version": "0003",
            "exchange_id": "binance_usdm",
            "symbols": symbols,
            "timeframe": timeframe,
            "months": months,
        }
        d_hash = dataset_hash(manifest)
        run_id = str(uuid.uuid4())
        engine_sha = git_head_sha()

        bundle = {
            "id": run_id,
            "experiment_code": experiment_code,
            "variant": variant,
            "run_kind": run_kind,
            "engine_git_sha": engine_sha,
            "config_hash": cfg_h,
            "config_snapshot": cfg.model_dump(mode="json"),
            "universe_hash": u_hash,
            "universe_snapshot": uni,
            "dataset_hash": d_hash,
            "dataset_manifest": manifest,
            "dataset_version_id": dataset_version_id,
            "feature_manifest": fm,
            "feature_manifest_hash": fm_hash,
            "exchange_id": "binance_usdm",
            "symbols": symbols,
            "timeframe": timeframe,
            "months": months,
            "metrics": metrics,
            "status": "succeeded",
            "created_at": _utcnow().isoformat(),
        }

        self._write_artifact(run_id, bundle)
        self._persist_run_if_enabled(experiment_code, bundle)
        return bundle

    def _write_artifact(self, run_id: str, bundle: dict[str, Any]) -> None:
        root = self.ARTIFACT_ROOT / run_id
        root.mkdir(parents=True, exist_ok=True)
        (root / "manifest.json").write_text(json.dumps(bundle, indent=2, default=str))

    def _persist_run_if_enabled(self, experiment_code: str, bundle: dict[str, Any]) -> None:
        from research_platform.config import get_research_settings

        if not get_research_settings().research_db_enabled:
            return

        from sqlalchemy import select

        from research_platform.db.session import research_session
        from research_platform.models.governance import Experiment, ExperimentRun

        with research_session() as session:
            if session is None:
                return
            exp = session.scalar(select(Experiment).where(Experiment.code == experiment_code))
            if exp is None:
                exp = Experiment(
                    id=str(uuid.uuid4()),
                    code=experiment_code,
                    title=experiment_code,
                    status="active",
                    created_at=_utcnow(),
                    updated_at=_utcnow(),
                )
                session.add(exp)
                session.flush()

            now = _utcnow()
            period_end = now
            period_start = now
            session.add(
                ExperimentRun(
                    id=bundle["id"],
                    experiment_id=exp.id,
                    variant=bundle["variant"],
                    run_kind=bundle["run_kind"],
                    engine_git_sha=bundle["engine_git_sha"],
                    config_hash=bundle["config_hash"],
                    config_snapshot=bundle["config_snapshot"],
                    universe_hash=bundle["universe_hash"],
                    universe_snapshot=bundle["universe_snapshot"],
                    dataset_hash=bundle["dataset_hash"],
                    dataset_manifest=bundle["dataset_manifest"],
                    dataset_version_id=bundle.get("dataset_version_id"),
                    feature_manifest=bundle["feature_manifest"],
                    feature_manifest_hash=bundle["feature_manifest_hash"],
                    exchange_id=bundle["exchange_id"],
                    symbols=bundle["symbols"],
                    timeframe=bundle["timeframe"],
                    period_start=period_start,
                    period_end=period_end,
                    months=bundle.get("months"),
                    metrics=bundle["metrics"],
                    artifacts_uri=str(self.ARTIFACT_ROOT / bundle["id"]),
                    status="succeeded",
                    created_at=now,
                    completed_at=now,
                )
            )
