from __future__ import annotations

import time
from typing import Any, Callable, TypeVar

from cachetools import TTLCache

from api.settings import get_settings

T = TypeVar("T")

_verdict_cache: TTLCache = TTLCache(maxsize=256, ttl=60)
_orderbook_cache: TTLCache = TTLCache(maxsize=64, ttl=10)


def _configure_caches() -> None:
    settings = get_settings()
    global _verdict_cache, _orderbook_cache
    _verdict_cache = TTLCache(maxsize=256, ttl=settings.verdict_cache_ttl_sec)
    _orderbook_cache = TTLCache(maxsize=64, ttl=settings.orderbook_cache_ttl_sec)


_configure_caches()


def cached_verdict(key: str, loader: Callable[[], T]) -> T:
    if key in _verdict_cache:
        return _verdict_cache[key]
    value = loader()
    _verdict_cache[key] = value
    return value


def cached_orderbook(key: str, loader: Callable[[], T]) -> T:
    if key in _orderbook_cache:
        return _orderbook_cache[key]
    value = loader()
    _orderbook_cache[key] = value
    return value


def cache_stats() -> dict[str, Any]:
    return {
        "verdict_entries": len(_verdict_cache),
        "orderbook_entries": len(_orderbook_cache),
        "server_time_utc": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
    }
