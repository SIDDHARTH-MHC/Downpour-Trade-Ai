from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx

from api.db import Database
from api.settings import get_settings

logger = logging.getLogger("downpour.alerts")

_recent_alerts: dict[tuple[str, str], datetime] = {}


async def send_telegram_alert(verdict: dict) -> None:
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return

    symbol = verdict.get("symbol", "?")
    action = verdict.get("action", "NO_TRADE")
    key = (symbol, action)
    now = datetime.now(timezone.utc)
    last = _recent_alerts.get(key)
    if last and (now - last).total_seconds() < 4 * 3600:
        return

    plan = verdict.get("trade_plan") or {}
    text = (
        f"Downpour Trade AI\n"
        f"{symbol} · {verdict.get('timeframe')} · {action}\n"
        f"Score: {verdict.get('weighted_score')} · {verdict.get('confidence')}\n"
        f"Entry: {plan.get('entry')} SL: {plan.get('stop_loss')} TP1: {plan.get('tp1')}"
    )
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json={"chat_id": settings.telegram_chat_id, "text": text})
    _recent_alerts[key] = now


async def alert_scan_hits(results: list[dict]) -> None:
    for verdict in results:
        if verdict.get("action") in {"LONG", "SHORT"}:
            await send_telegram_alert(verdict)
