"""Read-only market context (news, ETF notes) — never fed into synthesizer."""

from __future__ import annotations

import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

from api.settings import get_settings

_news_cache: dict[str, Any] = {}
_news_cache_at: float = 0.0


def fetch_news(symbol: str, limit: int = 8) -> dict[str, Any]:
    global _news_cache, _news_cache_at
    base = symbol.split("/")[0]
    cache_key = base
    now = time.time()
    if _news_cache.get(cache_key) and now - _news_cache_at < 900:
        return _news_cache[cache_key]

    settings = get_settings()
    headlines: list[dict] = []

    token = settings.cryptopanic_api_key or ""
    if token:
        try:
            url = (
                f"https://cryptopanic.com/api/v1/posts/?auth_token={token}"
                f"&currencies={base}&filter=important&public=true"
            )
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = json.loads(resp.read().decode())
            for post in (data.get("results") or [])[:limit]:
                headlines.append(
                    {
                        "title": post.get("title"),
                        "url": post.get("url"),
                        "source": (post.get("source") or {}).get("title"),
                        "sentiment": post.get("vote"),
                    }
                )
        except Exception as exc:  # noqa: BLE001
            headlines.append({"title": f"CryptoPanic fetch failed: {exc}", "url": None, "source": "system"})

    if not headlines:
        try:
            req = urllib.request.Request(
                "https://www.coindesk.com/arc/outboundfeeds/rss/",
                headers={"User-Agent": "DownpourTradeAI/1.0"},
            )
            with urllib.request.urlopen(req, timeout=12) as resp:
                root = ET.fromstring(resp.read())
            pattern = re.compile(re.escape(base), re.I)
            for item in root.findall(".//item")[:40]:
                title_el = item.find("title")
                link_el = item.find("link")
                if title_el is None or title_el.text is None:
                    continue
                title = title_el.text.strip()
                if base != "BTC" and not pattern.search(title):
                    continue
                headlines.append(
                    {
                        "title": title,
                        "url": link_el.text if link_el is not None else None,
                        "source": "CoinDesk RSS",
                        "sentiment": "neutral",
                    }
                )
                if len(headlines) >= limit:
                    break
        except Exception as exc:  # noqa: BLE001
            headlines = [{"title": f"News unavailable: {exc}", "url": None, "source": "system"}]

    out = {
        "symbol": symbol,
        "base": base,
        "headlines": headlines[:limit],
        "disclaimer": "Context only — does not affect engine scores.",
    }
    _news_cache[cache_key] = out
    _news_cache_at = now
    return out


def fetch_etf_context() -> dict[str, Any]:
    """Spot BTC ETF flow data requires a licensed feed; provide reference context only."""
    return {
        "status": "reference_only",
        "message": "Live ETF flow totals require a premium data provider. Use as macro context alongside BTC price action.",
        "reference_tickers": ["IBIT", "FBTC", "GBTC", "ARKB"],
        "disclaimer": "Not used in signals. Whale/ETF dashboards deferred until data SLA exists.",
    }
