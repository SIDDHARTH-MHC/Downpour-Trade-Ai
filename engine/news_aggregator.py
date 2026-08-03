"""Multi-source RSS news aggregator — context only, never fed to synthesizer."""

from __future__ import annotations

import hashlib
import json
import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Category = Literal["news", "macro", "exchange"]
FetchKind = Literal["rss", "bybit_api", "okx_api"]

USER_AGENT = "DownpourTradeAI/1.0 (+https://downpourtrade.shop; context-only aggregator)"


@dataclass
class FeedSource:
    feed_id: str
    name: str
    category: Category
    url: str | None = None
    kind: FetchKind = "rss"


# Public RSS + official exchange announcement APIs (context-only; links point to publisher).
FEED_SOURCES: list[FeedSource] = [
    # Crypto news
    FeedSource("coindesk", "CoinDesk", "news", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
    FeedSource("cointelegraph", "Cointelegraph", "news", "https://cointelegraph.com/rss"),
    FeedSource("theblock", "The Block", "news", "https://www.theblock.co/rss.xml"),
    FeedSource("bitcoinmagazine", "Bitcoin Magazine", "news", "https://bitcoinmagazine.com/feed"),
    FeedSource("coinbase_blog", "Coinbase Blog", "news", "https://www.coinbase.com/blog/rss.xml"),
    FeedSource("ethereum_blog", "Ethereum Foundation", "news", "https://blog.ethereum.org/feed.xml"),
    # Macroeconomics
    FeedSource("fed_press", "Federal Reserve", "macro", "https://www.federalreserve.gov/feeds/press_all.xml"),
    FeedSource("fed_monetary", "Fed / FOMC", "macro", "https://www.federalreserve.gov/feeds/press_monetary.xml"),
    FeedSource(
        "ecb_press",
        "ECB",
        "macro",
        "https://www.ecb.europa.eu/press/govc/pressconf/html/index_include.en.rss",
    ),
    FeedSource("boj_whatsnew", "Bank of Japan", "macro", "https://www.boj.or.jp/en/whatsnew/whatsnew.xml"),
    FeedSource(
        "treasury_press",
        "US Treasury",
        "macro",
        "https://home.treasury.gov/system/files/136/TreasuryPressRSS.xml",
    ),
    FeedSource("bls_releases", "BLS (CPI/PPI)", "macro", "https://www.bls.gov/feed/bls_latest.rss"),
    # Exchange announcements
    FeedSource("binance_ann", "Binance", "exchange", "https://www.binance.com/en/support/announcement/rss"),
    FeedSource("bybit_ann", "Bybit", "exchange", kind="bybit_api"),
    FeedSource("okx_ann", "OKX", "exchange", kind="okx_api"),
]


@dataclass
class NewsArticle:
    title: str
    url: str | None
    source: str
    category: Category
    published: str | None = None
    symbols: list[str] = field(default_factory=list)
    sentiment: str = "Neutral"  # Bullish | Bearish | Neutral


SYMBOL_PATTERNS: dict[str, list[str]] = {
    "BTC": [r"\bbitcoin\b", r"\bbtc\b", r"\$btc\b"],
    "ETH": [r"\bethereum\b", r"\beth\b", r"\$eth\b"],
    "SOL": [r"\bsolana\b", r"\bsol\b", r"\$sol\b"],
    "XRP": [r"\bripple\b", r"\bxrp\b", r"\$xrp\b"],
    "DOGE": [r"\bdogecoin\b", r"\bdoge\b", r"\$doge\b"],
    "BNB": [r"\bbnb\b", r"\bbinance coin\b"],
    "ADA": [r"\bcardano\b", r"\bada\b"],
    "AVAX": [r"\bavalanche\b", r"\bavax\b"],
    "DOT": [r"\bpolkadot\b", r"\bdot\b"],
    "MATIC": [r"\bpolygon\b", r"\bmatic\b"],
}

BULLISH_WORDS = (
    "surge",
    "rally",
    "soar",
    "approval",
    "approved",
    "inflow",
    "record high",
    "breakout",
    "bullish",
    "upgrade",
    "partnership",
    "launch",
    "etf inflow",
    "rate cut",
    "dovish",
)

BEARISH_WORDS = (
    "crash",
    "plunge",
    "hack",
    "exploit",
    "lawsuit",
    "sec sues",
    "ban",
    "outflow",
    "bearish",
    "bankruptcy",
    "liquidation",
    "delist",
    "halt",
    "rate hike",
    "hawkish",
    "inflation hot",
    "cpi hot",
)

_cache_articles: list[NewsArticle] | None = None
_cache_at: float = 0.0
CACHE_TTL_SEC = 900


def _strip_ns(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def _fetch_bytes(url: str, timeout: int = 14) -> bytes | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except (urllib.error.URLError, TimeoutError, ET.ParseError):
        return None


def _fetch_json(url: str, timeout: int = 18) -> dict | list | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return None


def _ms_to_pub(ms: int | str | None) -> str | None:
    if ms is None:
        return None
    try:
        ts = int(ms)
        if ts > 10_000_000_000:
            ts //= 1000
        return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OSError):
        return None


def _make_article(
    source: FeedSource,
    title: str,
    url: str | None,
    published: str | None,
    extra_text: str = "",
) -> NewsArticle:
    blob = f"{title} {extra_text}".strip()
    syms = tag_symbols(blob)
    if source.category == "news" and "ethereum" in source.feed_id:
        syms = sorted(set(syms + ["ETH"]))
    if "bitcoin" in source.feed_id.lower():
        syms = sorted(set(syms + ["BTC"]))
    return NewsArticle(
        title=title,
        url=url,
        source=source.name,
        category=source.category,
        published=published,
        symbols=syms,
        sentiment=tag_sentiment(blob),
    )


def _fetch_bybit(source: FeedSource, max_items: int = 15) -> list[NewsArticle]:
    raw = _fetch_json(
        "https://api.bybit.com/v5/announcements/index?locale=en-US&limit=" + str(max_items)
    )
    if not isinstance(raw, dict):
        return []
    items = (raw.get("result") or {}).get("list") or []
    articles: list[NewsArticle] = []
    for item in items[:max_items]:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        url = item.get("url")
        pub = _ms_to_pub(item.get("publishTime") or item.get("dateTimestamp"))
        desc = (item.get("description") or "").strip()
        articles.append(_make_article(source, title, url, pub, desc))
    return articles


def _fetch_okx(source: FeedSource, max_items: int = 15) -> list[NewsArticle]:
    raw = _fetch_json(f"https://www.okx.com/api/v5/support/announcements?page=1&limit={max_items}")
    if not isinstance(raw, dict) or raw.get("code") != "0":
        return []
    pages = raw.get("data") or []
    details: list[dict] = []
    for page in pages:
        if isinstance(page, dict):
            details.extend(page.get("details") or [])
    articles: list[NewsArticle] = []
    for item in details[:max_items]:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        url = item.get("url")
        pub = _ms_to_pub(item.get("businessPTime") or item.get("pTime"))
        articles.append(_make_article(source, title, url, pub))
    return articles


def _parse_rss_items(root: ET.Element) -> list[tuple[str, str | None, str | None]]:
    items: list[tuple[str, str | None, str | None]] = []
    for elem in root.iter():
        tag = _strip_ns(elem.tag)
        if tag not in {"item", "entry"}:
            continue
        title = link = pub = None
        for child in elem:
            ctag = _strip_ns(child.tag)
            if ctag == "title" and child.text:
                title = child.text.strip()
            elif ctag == "link":
                if child.text and child.text.strip().startswith("http"):
                    link = child.text.strip()
                elif child.get("href"):
                    link = child.get("href")
            elif ctag in {"pubDate", "published", "updated"} and child.text:
                pub = child.text.strip()
        if title:
            items.append((title, link, pub))
    return items


def _normalize_title(title: str) -> str:
    t = title.lower()
    t = re.sub(r"[^\w\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _dedupe_key(title: str, url: str | None) -> str:
    if url:
        return hashlib.sha256(url.encode()).hexdigest()[:16]
    return hashlib.sha256(_normalize_title(title).encode()).hexdigest()[:16]


def tag_symbols(text: str) -> list[str]:
    found: list[str] = []
    lower = text.lower()
    for sym, patterns in SYMBOL_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, lower, re.I):
                found.append(sym)
                break
    return sorted(set(found))


def tag_sentiment(text: str) -> str:
    lower = text.lower()
    bull = sum(1 for w in BULLISH_WORDS if w in lower)
    bear = sum(1 for w in BEARISH_WORDS if w in lower)
    if bull > bear and bull > 0:
        return "Bullish"
    if bear > bull and bear > 0:
        return "Bearish"
    return "Neutral"


def _fetch_feed(source: FeedSource, max_items: int = 15) -> list[NewsArticle]:
    if source.kind == "bybit_api":
        return _fetch_bybit(source, max_items=max_items)
    if source.kind == "okx_api":
        return _fetch_okx(source, max_items=max_items)
    if not source.url:
        return []
    raw = _fetch_bytes(source.url)
    if not raw:
        return []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return []
    articles: list[NewsArticle] = []
    for title, link, pub in _parse_rss_items(root)[:max_items]:
        articles.append(_make_article(source, title, link, pub))
    return articles


def aggregate_news(force_refresh: bool = False) -> list[NewsArticle]:
    global _cache_articles, _cache_at
    now = time.time()
    if not force_refresh and _cache_articles is not None and now - _cache_at < CACHE_TTL_SEC:
        return _cache_articles

    seen: set[str] = set()
    merged: list[NewsArticle] = []
    for source in FEED_SOURCES:
        try:
            batch = _fetch_feed(source)
        except Exception:  # noqa: BLE001
            continue
        for art in batch:
            key = _dedupe_key(art.title, art.url)
            if key in seen:
                continue
            seen.add(key)
            merged.append(art)

    merged.sort(key=lambda a: (a.category, a.title))
    _cache_articles = merged
    _cache_at = now
    return merged


def articles_for_symbol(symbol: str, limit: int = 12) -> list[NewsArticle]:
    base = symbol.split("/")[0].upper()
    all_articles = aggregate_news()
    matched: list[NewsArticle] = []
    general: list[NewsArticle] = []

    for art in all_articles:
        if base in art.symbols or (base == "BTC" and not art.symbols and art.category == "macro"):
            matched.append(art)
        elif base in art.title.upper() or re.search(rf"\b{re.escape(base)}\b", art.title, re.I):
            matched.append(art)
        elif art.category == "macro":
            general.append(art)

    if len(matched) < limit:
        for art in all_articles:
            if art.category == "news" and art not in matched:
                matched.append(art)
            if len(matched) >= limit:
                break

    if len(matched) < limit:
        matched.extend(general[: limit - len(matched)])

    return matched[:limit]


def article_to_dict(art: NewsArticle) -> dict:
    return {
        "title": art.title,
        "url": art.url,
        "source": art.source,
        "category": art.category,
        "published": art.published,
        "symbols": art.symbols,
        "sentiment": art.sentiment,
    }


def news_payload(symbol: str, limit: int = 12, category: str | None = None) -> dict[str, object]:
    base = symbol.split("/")[0]
    articles = aggregate_news()
    if category in {"news", "macro", "exchange"}:
        articles = [a for a in articles if a.category == category]
    elif symbol:
        articles = articles_for_symbol(symbol, limit=limit)
    else:
        articles = articles[:limit]

    if category in {"news", "macro", "exchange"}:
        articles = articles[:limit]

    return {
        "symbol": symbol,
        "base": base,
        "aggregated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "feed_count": len(FEED_SOURCES),
        "headlines": [article_to_dict(a) for a in articles],
        "disclaimer": "Context only — headlines link to original publishers (RSS/API); does not affect engine scores.",
    }
