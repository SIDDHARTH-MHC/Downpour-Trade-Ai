"""Read-only market context — news via owned RSS aggregator."""

from __future__ import annotations

from typing import Any

from engine.context_data import (
    fetch_etf_reference_context,
    fetch_liquidations_context as _liquidations,
    fetch_onchain_context as _onchain,
)
from engine.news_aggregator import news_payload


def fetch_news(symbol: str, limit: int = 12, category: str | None = None) -> dict[str, Any]:
    return news_payload(symbol, limit=limit, category=category)


def fetch_etf_context() -> dict[str, Any]:
    return fetch_etf_reference_context()


def fetch_liquidations_context(symbol: str = "BTC/USDT") -> dict[str, Any]:
    return _liquidations(symbol)


def fetch_onchain_context() -> dict[str, Any]:
    return _onchain()
