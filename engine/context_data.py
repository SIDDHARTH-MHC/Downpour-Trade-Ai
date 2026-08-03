"""Public context feeds (dashboard / trust disclaimers — not lane scores)."""

from __future__ import annotations

import json
import math
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

from engine.macro_context import _fetch_stooq_daily


def _http_json(url: str, timeout: float = 12.0) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "DownpourTradeAI/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode())


def _futures_symbol(symbol: str) -> str:
    return symbol.replace("/", "")


def _zscore(series: list[float]) -> tuple[float, float, float]:
    if len(series) < 3:
        return series[-1] if series else 0.0, 0.0, 0.0
    mean = sum(series) / len(series)
    var = sum((x - mean) ** 2 for x in series) / len(series)
    std = math.sqrt(var)
    last = series[-1]
    if std <= 0:
        return last, mean, 0.0
    return last, mean, (last - mean) / std


def fetch_taker_stress(symbol: str, period: str = "1h", limit: int = 48) -> dict[str, Any]:
    """Binance taker buy/sell volumes — proxy for forced-flow / liquidation stress (labeled estimate)."""
    sym = _futures_symbol(symbol)
    qs = urllib.parse.urlencode({"symbol": sym, "period": period, "limit": limit})
    url = f"https://fapi.binance.com/futures/data/takerlongshortRatio?{qs}"
    try:
        rows = _http_json(url)
    except Exception as exc:  # noqa: BLE001
        return {"symbol": symbol, "error": str(exc)}

    if not isinstance(rows, list) or not rows:
        return {"symbol": symbol, "error": "no taker ratio data"}

    sell_vols: list[float] = []
    buy_vols: list[float] = []
    for row in rows:
        try:
            sell_vols.append(float(row.get("sellVol", 0)))
            buy_vols.append(float(row.get("buyVol", 0)))
        except (TypeError, ValueError):
            continue

    if len(sell_vols) < 5:
        return {"symbol": symbol, "error": "insufficient taker history"}

    _, _, sell_z = _zscore(sell_vols)
    last_sell = sell_vols[-1]
    last_buy = buy_vols[-1]
    ratio = last_buy / last_sell if last_sell > 0 else None

    price_usd: float | None = None
    try:
        tick = _http_json(f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={sym}")
        price_usd = float(tick.get("price", 0))
    except Exception:
        price_usd = None

    est_liq_notional_usd: float | None = None
    if price_usd and price_usd > 0:
        # Base-asset sell volume × mark — rough 1h taker sell notional, not full liquidation map.
        est_liq_notional_usd = last_sell * price_usd

    elevated = sell_z >= 2.0
    return {
        "symbol": symbol,
        "period": period,
        "samples": len(sell_vols),
        "taker_buy_sell_ratio": ratio,
        "sell_volume_base_1h": last_sell,
        "buy_volume_base_1h": last_buy,
        "sell_volume_zscore": sell_z,
        "estimated_sell_notional_usd_1h": est_liq_notional_usd,
        "elevated_forced_flow": elevated,
        "source": "binance_futures_taker_ratio",
        "label": "exchange_estimated",
    }


def fetch_liquidations_context(symbol: str = "BTC/USDT") -> dict[str, Any]:
    stress = fetch_taker_stress(symbol)
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    if stress.get("error"):
        return {
            "status": "reference_only",
            "symbol": symbol,
            "updated_at_utc": updated,
            "message": "Could not load Binance taker flow; premium heatmaps still require a vendor feed.",
            "disclaimer": "Not used in lane scores. Taker sell spikes are a liquidation-pressure proxy only.",
            "stress": stress,
        }

    msg = (
        f"Taker sell z={stress['sell_volume_zscore']:.2f} on {symbol} ({stress['period']}). "
        "Use as context for cascade risk — not a CoinGlass-style liquidation map."
    )
    return {
        "status": "exchange_estimated",
        "symbol": symbol,
        "updated_at_utc": updated,
        "message": msg,
        "elevated_forced_flow": stress.get("elevated_forced_flow", False),
        "disclaimer": "Not used in lane scores. See Research_Roadmap.md R6 Phase A.",
        "stress": stress,
    }


def fetch_onchain_context() -> dict[str, Any]:
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    out: dict[str, Any] = {
        "updated_at_utc": updated,
        "asset": "BTC",
        "status": "public_api",
        "disclaimer": "Context only — bar alignment weak at 1h; not used in lane scores (R9).",
    }
    try:
        fees = _http_json("https://mempool.space/api/v1/fees/recommended")
        out["fees_sat_vb"] = {
            "fastest": fees.get("fastestFee"),
            "half_hour": fees.get("halfHourFee"),
            "hour": fees.get("hourFee"),
        }
    except Exception as exc:  # noqa: BLE001
        out["fees_error"] = str(exc)

    try:
        stats = _http_json("https://api.blockchain.info/stats")
        out["market_price_usd"] = stats.get("market_price_usd")
        out["hash_rate"] = stats.get("hash_rate")
        out["n_transactions"] = stats.get("n_transactions")
        out["minutes_between_blocks"] = stats.get("minutes_between_blocks")
        out["source_chain"] = "blockchain.info"
    except Exception as exc:  # noqa: BLE001
        out["chain_stats_error"] = str(exc)

    try:
        mempool = _http_json("https://mempool.space/api/mempool")
        out["mempool_tx_count"] = mempool.get("count")
        out["mempool_vsize"] = mempool.get("vsize")
        out["source_mempool"] = "mempool.space"
    except Exception as exc:  # noqa: BLE001
        out["mempool_error"] = str(exc)

    if out.get("fees_error") and out.get("chain_stats_error"):
        out["status"] = "unavailable"
    return out


def fetch_etf_reference_context() -> dict[str, Any]:
    """Spot ETF proxies via Stooq daily bars — reference only, not licensed flow totals."""
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    tickers = [
        ("ibit.us", "IBIT"),
        ("fbtc.us", "FBTC"),
        ("gbtc.us", "GBTC"),
    ]
    proxies: list[dict[str, Any]] = []
    for stooq_sym, label in tickers:
        rows = _fetch_stooq_daily(stooq_sym)
        if len(rows) < 2:
            proxies.append({"ticker": label, "error": "no stooq data"})
            continue
        prev = rows[-2][1]
        last = rows[-1][1]
        pct = (last - prev) / prev if prev > 0 else None
        proxies.append(
            {
                "ticker": label,
                "last_close_usd": last,
                "daily_change_pct": pct,
                "source": "stooq_daily",
            }
        )

    has_data = any("last_close_usd" in p for p in proxies)
    return {
        "status": "reference_proxy" if has_data else "reference_only",
        "updated_at_utc": updated,
        "message": (
            "Licensed daily ETF flow totals are not wired. "
            "Stooq spot ETF closes shown as macro reference — not signal inputs."
        ),
        "reference_tickers": [p["ticker"] for p in proxies],
        "proxies": proxies,
        "disclaimer": "Not used in signals. Promote only after immutable licensed flow snapshots (R8).",
    }
