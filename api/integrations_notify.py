"""Discord / Slack webhook payloads for scan alerts."""

from __future__ import annotations

from typing import Any

import httpx


def _base_text(verdict: dict[str, Any]) -> str:
    plan = verdict.get("trade_plan") or {}
    return (
        f"**{verdict.get('symbol')}** · {verdict.get('timeframe')} · **{verdict.get('action')}**\n"
        f"Score: {verdict.get('weighted_score')} · {verdict.get('confidence')}\n"
        f"Entry: {plan.get('entry')} · SL: {plan.get('stop_loss')} · TP1: {plan.get('tp1')}"
    )


async def send_discord(webhook_url: str, verdict: dict[str, Any]) -> None:
    if not webhook_url:
        return
    payload = {
        "username": "Downpour Trade AI",
        "content": "Downpour signal (deterministic engine)",
        "embeds": [
            {
                "title": f"{verdict.get('symbol')} {verdict.get('action')}",
                "description": _base_text(verdict).replace("**", ""),
                "color": 3447003 if verdict.get("action") == "LONG" else 15158332,
            }
        ],
    }
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(webhook_url, json=payload)


async def send_slack(webhook_url: str, verdict: dict[str, Any]) -> None:
    if not webhook_url:
        return
    text = _base_text(verdict).replace("**", "*")
    payload = {"text": f"Downpour Trade AI\n{text}"}
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(webhook_url, json=payload)
