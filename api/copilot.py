"""Deterministic explain-only copilot (no LLM required)."""

from __future__ import annotations

from typing import Any


def explain_markdown(payload: dict[str, Any]) -> str:
    action = payload.get("action", "NO_TRADE")
    symbol = payload.get("symbol", "")
    lines = [f"# Why {action}? — {symbol}", ""]

    trust = payload.get("trust")
    if trust:
        lines.append("## Provable confidence")
        lines.append(f"- Label: {trust.get('confidence')}")
        wr = trust.get("historical_win_rate")
        if wr is not None:
            lines.append(f"- Historical win rate: {wr * 100:.1f}%")
        n = trust.get("backtested_trades")
        if n is not None:
            lines.append(f"- Backtested trades in bucket: {n}")
        pf = trust.get("profit_factor")
        if pf is not None:
            lines.append(f"- Profit factor: {pf:.2f}")
        lines.append("")

    exp = payload.get("explanation") or {}
    if exp.get("why"):
        lines.append("## Supporting evidence")
        for item in exp["why"]:
            lines.append(f"- {item}")
        lines.append("")

    if exp.get("why_not"):
        lines.append("## Why not / cautions")
        for item in exp["why_not"]:
            lines.append(f"- {item}")
        lines.append("")

    if exp.get("risk"):
        lines.append("## Risk & plan")
        for item in exp["risk"]:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("_Generated from engine JSON only — not trading advice._")
    return "\n".join(lines)
