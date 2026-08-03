from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

import httpx

from api.db import Database
from api.integrations_notify import send_discord, send_slack
from api.settings import get_settings

logger = logging.getLogger("downpour.alerts")

_recent_alerts: dict[tuple[str, str], datetime] = {}


def _matches_rule(verdict: dict, rule: dict) -> bool:
    if not bool(rule.get("enabled", 1)):
        return False
    action = verdict.get("action", "NO_TRADE")
    allowed = {a.strip() for a in (rule.get("actions") or "LONG,SHORT").split(",") if a.strip()}
    if action not in allowed:
        return False
    score = abs(float(verdict.get("weighted_score") or 0))
    if score < float(rule.get("min_score") or 0):
        return False
    needle = (rule.get("confidence_contains") or "").strip()
    if needle and needle.lower() not in (verdict.get("confidence") or "").lower():
        return False
    return True


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


async def _post_webhook(url: str, verdict: dict) -> None:
    if not url:
        return
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json=verdict)


async def _notify_integrations(verdict: dict) -> None:
    settings = get_settings()
    db = Database()
    urls = db.get_integration_urls()
    discord = urls.get("discord_webhook_url") or settings.discord_webhook_url
    slack = urls.get("slack_webhook_url") or settings.slack_webhook_url
    try:
        if discord:
            await send_discord(discord, verdict)
    except Exception as exc:  # noqa: BLE001
        logger.warning("discord notify failed: %s", exc)
    try:
        if slack:
            await send_slack(slack, verdict)
    except Exception as exc:  # noqa: BLE001
        logger.warning("slack notify failed: %s", exc)


async def alert_scan_hits(results: list[dict]) -> None:
    db = Database()
    rules = db.list_alert_rules()
    use_rules = [r for r in rules if r.get("enabled")]

    for verdict in results:
        if verdict.get("action") not in {"LONG", "SHORT"}:
            continue
        matched = False
        if use_rules:
            for rule in use_rules:
                if not _matches_rule(verdict, rule):
                    continue
                matched = True
                if bool(rule.get("telegram", 1)):
                    await send_telegram_alert(verdict)
                webhook = (rule.get("webhook_url") or "").strip()
                if webhook:
                    await _post_webhook(webhook, verdict)
            if matched:
                await _notify_integrations(verdict)
        else:
            await send_telegram_alert(verdict)
            await _notify_integrations(verdict)
