"""Market data fetch, cache, and validation."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import ccxt
import pandas as pd

from engine.config import EngineConfig, load_config


class StaleDataError(Exception):
    """Raised when OHLCV data is too old for analysis."""


class DataFetchError(Exception):
    """Raised when market data cannot be fetched after retries."""


TIMEFRAME_MS: dict[str, int] = {
    "1m": 60_000,
    "3m": 180_000,
    "5m": 300_000,
    "15m": 900_000,
    "30m": 1_800_000,
    "1h": 3_600_000,
    "2h": 7_200_000,
    "4h": 14_400_000,
    "6h": 21_600_000,
    "12h": 43_200_000,
    "1d": 86_400_000,
}


def _utc_now_ms() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


class DataLayer:
    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or load_config()
        self.cache_dir = Path(self.config.data.cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.spot = ccxt.binance({"enableRateLimit": True})
        self.futures = ccxt.binanceusdm({"enableRateLimit": True})

    def _retry(self, fn, *args, **kwargs) -> Any:
        attempts = self.config.data.retry_attempts
        delay = self.config.data.retry_base_delay_sec
        last_error: Exception | None = None
        for i in range(attempts):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:  # noqa: BLE001 — ccxt raises many types
                last_error = exc
                if i < attempts - 1:
                    time.sleep(delay * (2**i))
        raise DataFetchError(f"Failed after {attempts} attempts: {last_error}") from last_error

    def _cache_path(self, symbol: str, tf: str, kind: str = "ohlcv") -> Path:
        safe = symbol.replace("/", "_")
        return self.cache_dir / f"{kind}_{safe}_{tf}.parquet"

    def _validate_freshness(self, df: pd.DataFrame, tf: str) -> None:
        if df.empty:
            raise StaleDataError("OHLCV dataframe is empty")
        if tf not in TIMEFRAME_MS:
            raise ValueError(f"Unsupported timeframe: {tf}")
        last_ts = int(df["timestamp"].iloc[-1])
        age_ms = _utc_now_ms() - last_ts
        max_age = TIMEFRAME_MS[tf] * self.config.data.staleness_multiplier
        if age_ms > max_age:
            raise StaleDataError(
                f"Stale OHLCV for {tf}: last candle age {age_ms}ms exceeds limit {max_age}ms"
            )

    def get_ohlcv(self, symbol: str, tf: str, bars: int | None = None, *, validate: bool = True) -> pd.DataFrame:
        bars = bars or self.config.data.ohlcv_bars
        cache_path = self._cache_path(symbol, tf)

        cached: pd.DataFrame | None = None
        if cache_path.exists():
            cached = pd.read_parquet(cache_path)
            cached["timestamp"] = cached["timestamp"].astype("int64")

        def fetch(limit: int, since: int | None = None) -> list[list[float]]:
            return self._retry(self.spot.fetch_ohlcv, symbol, tf, since=since, limit=limit)

        if cached is not None and len(cached) >= bars:
            tail_since = int(cached["timestamp"].iloc[-1]) - TIMEFRAME_MS[tf] * 5
            fresh_tail = fetch(limit=10, since=tail_since)
            if fresh_tail:
                tail_df = pd.DataFrame(fresh_tail, columns=["timestamp", "open", "high", "low", "close", "volume"])
                df = pd.concat([cached, tail_df], ignore_index=True)
                df = df.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")
                df = df.tail(bars).reset_index(drop=True)
            else:
                df = cached.tail(bars).reset_index(drop=True)
        else:
            raw = fetch(limit=min(bars, 1000))
            if len(raw) < bars:
                since = _utc_now_ms() - TIMEFRAME_MS[tf] * bars
                raw = fetch(limit=min(bars, 1000), since=since)
            df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])
            df = df.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")
            df = df.tail(bars).reset_index(drop=True)

        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype("float64")

        df.to_parquet(cache_path, index=False)
        if validate:
            self._validate_freshness(df, tf)
        return df

    def get_ohlcv_history(self, symbol: str, tf: str, bars: int, *, validate: bool = False) -> pd.DataFrame:
        """Fetch extended history for backtesting (may bypass staleness check)."""
        all_rows: list[list[float]] = []
        since: int | None = _utc_now_ms() - TIMEFRAME_MS.get(tf, 3_600_000) * bars
        remaining = bars
        while remaining > 0:
            chunk = self._retry(self.spot.fetch_ohlcv, symbol, tf, since=since, limit=min(remaining, 1000))
            if not chunk:
                break
            all_rows.extend(chunk)
            since = int(chunk[-1][0]) + 1
            remaining = bars - len(all_rows)
            if len(chunk) < 1000:
                break

        df = pd.DataFrame(all_rows, columns=["timestamp", "open", "high", "low", "close", "volume"])
        df = df.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")
        df = df.tail(bars).reset_index(drop=True)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = df[col].astype("float64")
        if validate and not df.empty:
            self._validate_freshness(df, tf)
        return df

    def get_funding(self, symbol: str) -> dict[str, Any]:
        futures_symbol = symbol.replace("/", "")
        try:
            current = self._retry(self.futures.fetch_funding_rate, futures_symbol)
            history = self._retry(self.futures.fetch_funding_rate_history, futures_symbol, limit=30)
            return {"current": current, "history": history}
        except Exception:
            return {"current": None, "history": []}

    def get_oi(self, symbol: str, tf: str = "1h") -> pd.DataFrame:
        futures_symbol = symbol.replace("/", "")
        try:
            raw = self._retry(self.futures.fetch_open_interest_history, futures_symbol, timeframe=tf, limit=48)
            if not raw:
                return pd.DataFrame(columns=["timestamp", "openInterestValue", "openInterestAmount"])
            df = pd.DataFrame(raw)
            if "timestamp" in df.columns:
                df["timestamp"] = df["timestamp"].astype("int64")
            return df
        except Exception:
            return pd.DataFrame(columns=["timestamp", "openInterestValue", "openInterestAmount"])

    def get_book(self, symbol: str, limit: int = 500) -> dict[str, Any]:
        return self._retry(self.spot.fetch_order_book, symbol, limit)

    def get_ticker(self, symbol: str) -> dict[str, Any]:
        return self._retry(self.spot.fetch_ticker, symbol)

    def get_mid_price(self, symbol: str) -> float:
        """Current mid price from ticker bid/ask."""
        ticker = self.get_ticker(symbol)
        bid = ticker.get("bid")
        ask = ticker.get("ask")
        if bid and ask:
            return float((bid + ask) / 2)
        last = ticker.get("last") or ticker.get("close")
        if last:
            return float(last)
        raise DataFetchError(f"No price available for {symbol}")

    def get_funding_history(self, symbol: str, limit: int = 200) -> list[dict[str, Any]]:
        futures_symbol = symbol.replace("/", "")
        try:
            return self._retry(self.futures.fetch_funding_rate_history, futures_symbol, limit=limit)
        except Exception:
            return []

    def get_oi_history(self, symbol: str, tf: str = "1h", limit: int = 500) -> pd.DataFrame:
        futures_symbol = symbol.replace("/", "")
        try:
            raw = self._retry(
                self.futures.fetch_open_interest_history,
                futures_symbol,
                timeframe=tf,
                limit=limit,
            )
            if not raw:
                return pd.DataFrame(columns=["timestamp", "openInterestValue", "openInterestAmount"])
            df = pd.DataFrame(raw)
            if "timestamp" in df.columns:
                df["timestamp"] = df["timestamp"].astype("int64")
            return df.sort_values("timestamp").reset_index(drop=True)
        except Exception:
            return pd.DataFrame(columns=["timestamp", "openInterestValue", "openInterestAmount"])

    def get_trades(self, symbol: str, limit: int = 200) -> list[dict[str, Any]]:
        try:
            return self._retry(self.spot.fetch_trades, symbol, limit=limit)
        except Exception:
            return []

    def get_top_volume_pairs(self, top_n: int = 20) -> list[str]:
        tickers = self._retry(self.spot.fetch_tickers)
        usdt_pairs = [
            (sym, info.get("quoteVolume") or 0)
            for sym, info in tickers.items()
            if sym.endswith("/USDT") and info.get("quoteVolume")
        ]
        usdt_pairs.sort(key=lambda x: x[1], reverse=True)
        return [sym for sym, _ in usdt_pairs[:top_n]]

    @staticmethod
    def htf_timeframe(tf: str, multiplier: int = 4) -> str:
        order = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"]
        if tf not in order:
            return "4h"
        idx = min(order.index(tf) + 2, len(order) - 1)
        return order[idx]

    @staticmethod
    def is_major(symbol: str) -> bool:
        base = symbol.split("/")[0]
        return base in {"BTC", "ETH"}
