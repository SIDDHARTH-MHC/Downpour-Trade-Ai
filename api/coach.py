"""Education-only coach — habits and engine literacy, never trade calls."""

from __future__ import annotations

from typing import Any


def coach_reply(message: str, context: dict[str, Any] | None = None) -> dict[str, str]:
    ctx = context or {}
    q = (message or "").strip().lower()
    symbol = ctx.get("symbol") or "this pair"
    action = ctx.get("action") or "NO_TRADE"

    if any(w in q for w in ("confirmation", "early", "fomo", "chase")):
        return {
            "topic": "process",
            "markdown": (
                "## Entering before confirmation\n\n"
                "The engine supports **patient** entries (limit near structure) vs market-style entries. "
                "If you tend to chase:\n"
                "- Wait for structure to stop flagging `no_edge`.\n"
                "- Prefer alerts when **score and confidence** both meet your rule (see Alerts).\n"
                "- Review **Replay** on the pair page to see what fired last.\n\n"
                f"Current `{symbol}` verdict: **{action}** — use that as context only, not a command to trade.\n\n"
                "_Educational only — not trading advice._"
            ),
        }

    if "no trade" in q or "no_trade" in q or "why wait" in q:
        return {
            "topic": "no_trade",
            "markdown": (
                "## Why NO-TRADE is normal\n\n"
                "Downpour defaults to **NO-TRADE** when lanes conflict, R:R is below minimum, "
                "regime is SHOCK, or structure has no edge. That selectivity is intentional.\n"
                "- Check **Scan explainability** on the dashboard for rejection counts.\n"
                "- Read `/engine` for when lanes are ignored.\n\n"
                "_Not trading advice._"
            ),
        }

    if "confidence" in q or "calibrat" in q or "trust" in q:
        return {
            "topic": "confidence",
            "markdown": (
                "## Understanding confidence\n\n"
                "Labels come from **walk-forward backtests**, not marketing tiers. "
                "See the Trust card: win rate, profit factor, trade count, walk-forward pass/fail.\n"
                "- Run calibration on **Backtests** if you see `INSUFFICIENT_DATA`.\n"
                "- Use **Confidence history** to see if labels matched outcomes.\n\n"
                "_Not trading advice._"
            ),
        }

    if "size" in q or "position" in q or "risk" in q or "1%" in q:
        return {
            "topic": "risk",
            "markdown": (
                "## Position sizing (how the engine thinks)\n\n"
                "Trade plans assume **~1% account risk** to stop distance (`config.yaml` → `risk.account_risk_pct`).\n"
                "- Portfolio page aggregates **open signal risk** at your equity input.\n"
                "- Scenarios stress-test open plans — not your full net worth.\n\n"
                "_Not trading advice._"
            ),
        }

    if "journal" in q or "note" in q or "review" in q:
        return {
            "topic": "journal",
            "markdown": (
                "## Research notebook habit\n\n"
                "After each signal you acted on (or skipped), log:\n"
                "1. What the engine said vs what you did.\n"
                "2. Whether you waited for confirmation.\n"
                "3. Outcome when resolved.\n\n"
                "Use the **Notebook** page — entries stay on the server (this deployment's SQLite).\n\n"
                "_Not trading advice._"
            ),
        }

    return {
        "topic": "general",
        "markdown": (
            "## AI Coach (education only)\n\n"
            "Ask about: **confirmation**, **NO-TRADE**, **confidence**, **position sizing**, **journal habits**.\n\n"
            "I do **not** give entries, stops, targets, or 'should I buy' answers. "
            "Use **Explain-only Copilot** on the pair page for verdict JSON paraphrasing.\n\n"
            f"Context: `{symbol}` · {action}\n\n"
            "_Not trading advice._"
        ),
    }
