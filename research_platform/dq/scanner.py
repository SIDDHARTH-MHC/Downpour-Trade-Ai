"""In-memory / dataframe data quality checks (reporting only — Phase 4)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

import pandas as pd

RUNNER_VERSION = "dq-1.0.0"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def scan_ohlcv_frame(
    df: pd.DataFrame,
    *,
    exchange_id: str = "binance_usdm",
    symbol: str = "BTC/USDT",
    timeframe: str = "1h",
    ts_col: str = "timestamp",
) -> dict[str, Any]:
    """Analyze OHLCV dataframe; returns report dict suitable for persistence."""
    report_id = str(uuid.uuid4())
    issues: list[dict[str, Any]] = []
    missing = duplicate = corrupt = gaps = 0

    if df.empty:
        return _report(
            report_id,
            exchange_id,
            symbol,
            timeframe,
            severity="blocking",
            missing=0,
            duplicate=0,
            corrupt=0,
            gaps=0,
            expected=0,
            actual=0,
            issues=[{"issue_type": "empty_frame", "severity": "blocking"}],
        )

    work = df.copy()
    if ts_col not in work.columns and "ts" in work.columns:
        ts_col = "ts"
    ts_series = pd.to_datetime(work[ts_col], unit="ms", utc=True, errors="coerce")
    if ts_series.isna().all():
        ts_series = pd.to_datetime(work[ts_col], utc=True, errors="coerce")
    work["_ts"] = ts_series

    duplicate = int(work["_ts"].duplicated().sum())
    if duplicate:
        issues.append({"issue_type": "duplicate_bar", "severity": "blocking", "count": duplicate})

    for col in ("open", "high", "low", "close"):
        if col not in work.columns:
            corrupt += 1
            issues.append({"issue_type": "missing_column", "severity": "blocking", "column": col})
            continue
    if all(c in work.columns for c in ("open", "high", "low", "close")):
        bad = (
            (work["high"] < work[["open", "close", "low"]].max(axis=1))
            | (work["low"] > work[["open", "close", "high"]].min(axis=1))
            | (work["close"] <= 0)
        )
        corrupt = int(bad.sum())
        if corrupt:
            issues.append({"issue_type": "ohlc_invalid", "severity": "blocking", "count": corrupt})

    sorted_ts = work["_ts"].dropna().sort_values()
    if len(sorted_ts) >= 2:
        deltas = sorted_ts.diff().dropna()
        if timeframe == "1h":
            expected_delta = pd.Timedelta(hours=1)
        elif timeframe == "4h":
            expected_delta = pd.Timedelta(hours=4)
        elif timeframe == "1d":
            expected_delta = pd.Timedelta(days=1)
        else:
            expected_delta = pd.Timedelta(hours=1)
        gap_mask = deltas > expected_delta * 1.5
        gaps = int(gap_mask.sum())
        if gaps:
            issues.append({"issue_type": "timestamp_gap", "severity": "warning", "count": gaps})

    actual = len(work)
    expected = actual  # without calendar grid we treat observed span as baseline
    severity = "ok"
    if duplicate or corrupt:
        severity = "blocking"
    elif gaps:
        severity = "warning"

    checksum = None
    if "close" in work.columns:
        import hashlib

        payload = work["close"].astype(str).str.cat(sep=",")
        checksum = hashlib.sha256(payload.encode()).hexdigest()[:32]

    return _report(
        report_id,
        exchange_id,
        symbol,
        timeframe,
        severity=severity,
        missing=missing,
        duplicate=duplicate,
        corrupt=corrupt,
        gaps=gaps,
        expected=expected,
        actual=actual,
        issues=issues,
        checksum=checksum,
    )


def _report(
    report_id: str,
    exchange_id: str,
    symbol: str,
    timeframe: str,
    *,
    severity: str,
    missing: int,
    duplicate: int,
    corrupt: int,
    gaps: int,
    expected: int,
    actual: int,
    issues: list[dict[str, Any]],
    checksum: str | None = None,
) -> dict[str, Any]:
    return {
        "id": report_id,
        "scope": "symbol_series",
        "exchange_id": exchange_id,
        "symbol": symbol,
        "series": f"candles_{timeframe}",
        "timeframe": timeframe,
        "run_at": _utcnow().isoformat(),
        "runner_version": RUNNER_VERSION,
        "expected_bars": expected,
        "actual_bars": actual,
        "missing_bars": missing,
        "duplicate_bars": duplicate,
        "gap_count": gaps,
        "corrupt_rows": corrupt,
        "checksum": checksum,
        "details": {"issues": issues},
        "severity": severity,
        "status": "open",
        "issues": issues,
    }
