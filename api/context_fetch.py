"""Read-only market context — news via owned RSS aggregator."""

from __future__ import annotations

from typing import Any

from engine.news_aggregator import news_payload


def fetch_news(symbol: str, limit: int = 12, category: str | None = None) -> dict[str, Any]:
    return news_payload(symbol, limit=limit, category=category)


def fetch_etf_context() -> dict[str, Any]:
    """Spot BTC ETF flow data requires a licensed feed; provide reference context only."""
    return {
        "status": "reference_only",
        "message": "Live ETF flow totals require a premium data provider. Use as macro context alongside BTC price action.",
        "reference_tickers": ["IBIT", "FBTC", "GBTC", "ARKB"],
        "disclaimer": "Not used in signals. Whale/ETF dashboards deferred until data SLA exists.",
    }


def fetch_liquidations_context() -> dict[str, Any]:
    """Liquidation aggregates require a vendor feed (e.g. CoinGlass). Dashboard/context only."""
    return {
        "status": "reference_only",
        "message": "Live liquidation heatmaps require a premium data provider. Label any future overlay as modeled/estimated.",
        "disclaimer": "Not used in lane scores. See Research_Roadmap.md R6.",
    }
