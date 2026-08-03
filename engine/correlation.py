"""Rolling correlation vs BTC for context panels (non-verdict)."""

from __future__ import annotations

import pandas as pd

from engine.config import EngineConfig, load_config
from engine.data import DataLayer


def correlation_vs_btc(symbol: str, tf: str = "1h", bars: int = 72, config: EngineConfig | None = None) -> dict:
    cfg = config or load_config()
    data = DataLayer(cfg)
    if symbol.startswith("BTC/"):
        return {"symbol": symbol, "beta_vs_btc": 1.0, "correlation": 1.0, "bars": bars}

    df = data.get_ohlcv(symbol, tf, bars=bars, validate=False)
    btc = data.get_ohlcv("BTC/USDT", tf, bars=bars, validate=False)
    if len(df) < 20 or len(btc) < 20:
        return {"symbol": symbol, "beta_vs_btc": None, "correlation": None, "bars": bars}

    merged = pd.merge(
        df[["timestamp", "close"]].rename(columns={"close": "sym"}),
        btc[["timestamp", "close"]].rename(columns={"close": "btc"}),
        on="timestamp",
        how="inner",
    )
    if len(merged) < 15:
        return {"symbol": symbol, "beta_vs_btc": None, "correlation": None, "bars": bars}

    sym_ret = merged["sym"].pct_change().dropna()
    btc_ret = merged["btc"].pct_change().dropna()
    aligned = pd.concat([sym_ret, btc_ret], axis=1).dropna()
    if len(aligned) < 10:
        return {"symbol": symbol, "beta_vs_btc": None, "correlation": None, "bars": bars}

    corr = float(aligned.iloc[:, 0].corr(aligned.iloc[:, 1]))
    btc_var = float(aligned.iloc[:, 1].var())
    beta = float(aligned.iloc[:, 0].cov(aligned.iloc[:, 1]) / btc_var) if btc_var > 0 else 0.0
    return {
        "symbol": symbol,
        "correlation": round(corr, 4),
        "beta_vs_btc": round(beta, 4),
        "bars": len(aligned),
        "timeframe": tf,
    }


def correlation_matrix(symbols: list[str], tf: str = "1h", config: EngineConfig | None = None) -> dict:
    rows = []
    for sym in symbols:
        try:
            rows.append(correlation_vs_btc(sym, tf, config=config))
        except Exception as exc:  # noqa: BLE001
            rows.append({"symbol": sym, "correlation": None, "beta_vs_btc": None, "error": str(exc)})
    return {"timeframe": tf, "benchmark": "BTC/USDT", "rows": rows}
