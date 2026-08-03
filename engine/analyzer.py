"""End-to-end analysis orchestration."""

from __future__ import annotations

from datetime import datetime, timezone

from engine.calibration import apply_confidence
from engine.config import EngineConfig, load_config
from engine.data import DataLayer
from engine.explanation import build_explanation
from engine.lanes.flow import analyze_flow
from engine.lanes.regime import analyze_regime
from engine.lanes.structure import analyze_structure
from engine.lanes.technical import analyze_technical
from engine.models import Verdict
from engine.risk import build_trade_plan
from engine.structure_events import detect_structure_events
from engine.synthesizer import synthesize


def analyze_symbol(
    symbol: str,
    tf: str = "1h",
    *,
    patient: bool = False,
    equity_usd: float | None = None,
    light: bool = False,
    config: EngineConfig | None = None,
) -> Verdict:
    cfg = config or load_config()
    data = DataLayer(cfg)
    bars = 200 if light else cfg.data.ohlcv_bars
    book_limit = 50 if light else 500

    df = data.get_ohlcv(symbol, tf, bars=bars)
    htf = data.get_ohlcv(symbol, DataLayer.htf_timeframe(tf, cfg.technical.htf_multiplier), bars=bars, validate=False)
    df_4h = data.get_ohlcv(symbol, "4h", bars=bars, validate=False)

    funding = data.get_funding(symbol)
    oi = data.get_oi(symbol, tf)
    book = data.get_book(symbol, limit=book_limit)
    trades = [] if light else data.get_trades(symbol)

    btc_df = None
    if symbol.split("/")[0] != "BTC":
        try:
            btc_df = data.get_ohlcv("BTC/USDT", "1h", bars=10, validate=False)
        except Exception:
            btc_df = None

    technical = analyze_technical(df, htf, cfg)
    flow = analyze_flow(df, funding, oi, trades, cfg)
    structure = analyze_structure(df, book, symbol, cfg)
    regime = analyze_regime(df, df_4h, symbol, btc_df, cfg, tf=tf)

    verdict = synthesize([technical, flow, structure], regime, cfg)
    verdict.structure_events = detect_structure_events(df, cfg.structure.swing_fractal)

    mid_price: float | None = None
    if light:
        mid_price = float(df["close"].iloc[-1])
    else:
        try:
            mid_price = data.get_mid_price(symbol)
        except Exception:
            mid_price = float(df["close"].iloc[-1])

    verdict = build_trade_plan(
        verdict, df, patient=patient, equity_usd=equity_usd, mid_price=mid_price, config=cfg
    )
    verdict = apply_confidence(verdict, config=cfg)
    verdict.explanation = build_explanation(verdict)

    last_ts = int(df["timestamp"].iloc[-1])
    verdict.symbol = symbol
    verdict.timeframe = tf
    verdict.timestamp = datetime.fromtimestamp(last_ts / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return verdict
