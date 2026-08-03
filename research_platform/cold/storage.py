"""Parquet export and offline DuckDB helpers (Phase 9 — research only)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_EXPORT_ROOT = Path("data/mds/parquet")


def export_candles_parquet(
    df: pd.DataFrame,
    *,
    exchange_id: str,
    symbol: str,
    timeframe: str,
    year: int,
    root: Path | None = None,
) -> Path:
    base = root or DEFAULT_EXPORT_ROOT
    sym = symbol.replace("/", "-")
    out_dir = base / f"exchange={exchange_id}" / f"timeframe={timeframe}" / f"year={year}" / f"symbol={sym}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "part-000.parquet"
    df.to_parquet(out_path, index=False)
    return out_path


def duckdb_query_parquet(sql: str, parquet_glob: str) -> list[dict[str, Any]]:
    """Offline research SQL over Parquet; never call from production API."""
    try:
        import duckdb
    except ImportError as exc:
        raise RuntimeError("duckdb is optional; pip install duckdb for offline research") from exc

    con = duckdb.connect(database=":memory:")
    con.execute(f"CREATE OR REPLACE VIEW mds AS SELECT * FROM read_parquet('{parquet_glob}')")
    result = con.execute(sql).fetchdf()
    return result.to_dict(orient="records")


def freeze_dataset_bundle(
    version_code: str,
    manifest: dict[str, Any],
    parquet_paths: list[Path],
    root: Path | None = None,
) -> Path:
    import json
    import shutil

    base = root or Path("data/datasets/v1")
    dest = base / version_code
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    for p in parquet_paths:
        target = dest / "parquet" / p.name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, target)
    return dest
