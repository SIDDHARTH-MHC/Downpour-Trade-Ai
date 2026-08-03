"""Aggregate NO-TRADE reasons from a scan batch."""

from __future__ import annotations

from collections import Counter
from typing import Any


def _bucket_reason(text: str) -> str:
    lower = text.lower()
    if "regime" in lower or "shock" in lower or "no-trade" in lower or "btc 1h" in lower:
        return "regime_block"
    if "conflict" in lower:
        return "lane_conflict"
    if "no_edge" in lower or "mid-range" in lower or "no structural" in lower:
        return "structure_no_edge"
    if "neutral band" in lower or "not aligned" in lower:
        return "weak_alignment"
    if "adverse" in lower:
        return "adverse_lane"
    if "weighted score" in lower and "within" in lower:
        return "score_neutral"
    return "other"


def summarize_scan(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    actionable = sum(1 for r in results if r.get("action") in {"LONG", "SHORT"})
    rejected = total - actionable
    buckets: Counter[str] = Counter()

    for row in results:
        if row.get("action") != "NO_TRADE":
            continue
        reasons = row.get("reasons") or []
        if not reasons:
            buckets["other"] += 1
            continue
        for reason in reasons:
            buckets[_bucket_reason(reason)] += 1

    return {
        "total_scanned": total,
        "actionable_count": actionable,
        "rejected_count": rejected,
        "rejection_reasons": dict(buckets.most_common()),
    }
