"""Historical replay and per-rule win-rate tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from engine.config import EngineConfig, load_config
from engine.data import DataLayer
from engine.lanes.flow import analyze_flow
from engine.lanes.regime import analyze_regime
from engine.lanes.structure import analyze_structure
from engine.lanes.technical import analyze_technical
from engine.models import LaneResult
from engine.risk import build_trade_plan
from engine.synthesizer import synthesize
from engine.utils import htf_factor, resample_ohlcv


def _funding_as_of(history: list[dict], ts: int) -> dict:
    prior = [h for h in history if int(h.get("timestamp") or 0) <= ts]
    if not prior:
        return {"current": None, "history": []}
    return {"current": prior[-1], "history": prior[-30:]}


def _oi_as_of(oi_df: pd.DataFrame, ts: int) -> pd.DataFrame:
    if oi_df.empty or "timestamp" not in oi_df.columns:
        return oi_df.iloc[:0]
    return oi_df[oi_df["timestamp"] <= ts].tail(48).reset_index(drop=True)


def _flow_for_backtest(
    window: pd.DataFrame,
    funding_history: list[dict],
    oi_df: pd.DataFrame,
    cfg: EngineConfig,
) -> LaneResult:
    ts = int(window["timestamp"].iloc[-1])
    funding = _funding_as_of(funding_history, ts)
    oi_slice = _oi_as_of(oi_df, ts)
    if funding.get("current") or len(oi_slice) >= 24:
        return analyze_flow(window, funding, oi_slice, trades=[], config=cfg)
    return LaneResult(
        name="flow",
        score=0.0,
        evidence=["backtest: flow lane skipped (no historical funding/OI at bar)"],
        values={},
    )


@dataclass
class TradeRecord:
    bar_index: int
    action: str
    entry: float
    stop_loss: float
    tp1: float
    outcome: str
    pnl_r: float
    weighted_score: float


@dataclass
class BacktestResult:
    symbol: str
    timeframe: str
    trades: list[TradeRecord] = field(default_factory=list)
    structure_degraded: bool = True
    flow_degraded: bool = False
    bucket_stats: dict = field(default_factory=dict)

    def summary(self) -> dict:
        if not self.trades:
            return {
                "trade_count": 0,
                "win_rate": 0.0,
                "avg_r": 0.0,
                "profit_factor": 0.0,
                "max_drawdown_r": 0.0,
                "structure_degraded": self.structure_degraded,
                "flow_degraded": self.flow_degraded,
                "bucket_stats": self.bucket_stats,
            }
        wins = [t for t in self.trades if t.outcome == "TP1"]
        gross_profit = sum(t.pnl_r for t in self.trades if t.pnl_r > 0)
        gross_loss = abs(sum(t.pnl_r for t in self.trades if t.pnl_r < 0))
        pf = gross_profit / gross_loss if gross_loss else float("inf")
        return {
            "trade_count": len(self.trades),
            "win_rate": len(wins) / len(self.trades),
            "avg_r": sum(t.pnl_r for t in self.trades) / len(self.trades),
            "profit_factor": pf,
            "max_drawdown_r": min(0, _running_dd([t.pnl_r for t in self.trades])),
            "structure_degraded": self.structure_degraded,
            "flow_degraded": self.flow_degraded,
            "bucket_stats": self.bucket_stats,
        }


def _running_dd(pnls: list[float]) -> float:
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for p in pnls:
        equity += p
        peak = max(peak, equity)
        max_dd = min(max_dd, equity - peak)
    return max_dd


def score_bucket(score: float, action: str) -> str:
    s = score if action == "LONG" else abs(score)
    if s >= 50:
        return "50+"
    if s >= 35:
        return "35-50"
    if s <= -50:
        return "-50-"
    if s <= -35:
        return "-50--35"
    return "neutral"


def bucket_stats_from_trades(trades: list[TradeRecord]) -> dict:
    buckets: dict[str, list[float]] = {}
    for trade in trades:
        bucket = score_bucket(trade.weighted_score, trade.action)
        buckets.setdefault(bucket, []).append(trade.pnl_r)

    stats: dict[str, dict] = {}
    for bucket, pnls in buckets.items():
        wins = sum(1 for p in pnls if p > 0)
        gross_profit = sum(p for p in pnls if p > 0)
        gross_loss = abs(sum(p for p in pnls if p < 0))
        stats[bucket] = {
            "trade_count": len(pnls),
            "win_rate": wins / len(pnls) if pnls else 0,
            "avg_r": sum(pnls) / len(pnls) if pnls else 0,
            "profit_factor": gross_profit / gross_loss if gross_loss else float("inf"),
            "max_drawdown_r": min(0, _running_dd(pnls)),
        }
    return stats


def _simulate_outcome(
    df: pd.DataFrame,
    start_idx: int,
    action: str,
    entry: float,
    sl: float,
    tp1: float,
    timeout: int,
    fee_pct: float,
    slippage_pct: float,
) -> tuple[str, float]:
    cost = fee_pct + slippage_pct
    end = min(start_idx + 1 + timeout, len(df))
    for j in range(start_idx + 1, end):
        high = df["high"].iloc[j]
        low = df["low"].iloc[j]
        if action == "LONG":
            if low <= sl:
                return "SL", -1.0 - cost
            if high >= tp1:
                return "TP1", abs(tp1 - entry) / abs(entry - sl) - cost
        else:
            if high >= sl:
                return "SL", -1.0 - cost
            if low <= tp1:
                return "TP1", abs(entry - tp1) / abs(sl - entry) - cost
    last = df["close"].iloc[end - 1]
    if action == "LONG":
        pnl = (last - entry) / abs(entry - sl) - cost
    else:
        pnl = (entry - last) / abs(sl - entry) - cost
    return "TIMEOUT", pnl if pnl < 0 else -cost


def run_backtest(
    symbol: str,
    tf: str,
    months: int = 12,
    config: EngineConfig | None = None,
    *,
    start_bar: int | None = None,
    end_bar: int | None = None,
    df: pd.DataFrame | None = None,
    funding_history: list[dict] | None = None,
    oi_full: pd.DataFrame | None = None,
) -> BacktestResult:
    cfg = config or load_config()
    data = DataLayer(cfg)
    bars_per_month = 30 * 24 if tf == "1h" else 30 * 24 * 4
    bars = months * bars_per_month
    if df is None:
        df = data.get_ohlcv_history(symbol, tf, bars=bars, validate=False)
    if funding_history is None:
        funding_history = data.get_funding_history(symbol, limit=500)
    if oi_full is None:
        oi_full = data.get_oi_history(symbol, tf, limit=500)
    flow_available = bool(funding_history) or len(oi_full) >= 24

    htf_tf = DataLayer.htf_timeframe(tf, cfg.technical.htf_multiplier)
    htf_f = htf_factor(tf, htf_tf)
    tf4_f = htf_factor(tf, "4h")

    result = BacktestResult(symbol=symbol, timeframe=tf, structure_degraded=True, flow_degraded=not flow_available)
    warmup = 220
    timeout = cfg.risk.trade_timeout_bars
    i_start = start_bar if start_bar is not None else warmup
    i_end = end_bar if end_bar is not None else len(df) - timeout - 1

    for i in range(i_start, i_end):
        window = df.iloc[: i + 1].copy()
        htf_window = resample_ohlcv(window, htf_f)
        df_4h = resample_ohlcv(window, tf4_f)

        technical = analyze_technical(window, htf_window, cfg)
        regime = analyze_regime(window, df_4h, symbol, None, cfg, tf=tf)
        flow = _flow_for_backtest(window, funding_history, oi_full, cfg)
        structure = analyze_structure(window, book=None, symbol=symbol, config=cfg)
        verdict = synthesize([technical, flow, structure], regime, cfg)
        mid = float(window["close"].iloc[-1])
        verdict = build_trade_plan(verdict, window, mid_price=mid, config=cfg)

        if verdict.action == "NO_TRADE" or verdict.trade_plan is None:
            continue

        plan = verdict.trade_plan
        outcome, pnl_r = _simulate_outcome(
            df,
            i,
            verdict.action,
            plan.entry,
            plan.stop_loss,
            plan.tp1,
            timeout,
            cfg.backtest.fee_pct,
            cfg.backtest.slippage_pct,
        )
        result.trades.append(
            TradeRecord(
                bar_index=i,
                action=verdict.action,
                entry=plan.entry,
                stop_loss=plan.stop_loss,
                tp1=plan.tp1,
                outcome=outcome,
                pnl_r=pnl_r,
                weighted_score=verdict.weighted_score,
            )
        )

    result.bucket_stats = bucket_stats_from_trades(result.trades)
    return result


def _bars_per_month(tf: str) -> int:
    if tf == "1h":
        return 30 * 24
    if tf == "15m":
        return 30 * 24 * 4
    if tf == "4h":
        return 30 * 6
    return 30 * 24


def run_walk_forward(
    symbol: str,
    tf: str,
    months: int = 18,
    config: EngineConfig | None = None,
) -> dict:
    """Walk-forward validation: OOS trades only feed calibration (§11)."""
    cfg = config or load_config()
    bpm = _bars_per_month(tf)
    total_bars = months * bpm
    train_bars = cfg.backtest.walk_forward_train_months * bpm
    val_bars = cfg.backtest.walk_forward_val_months * bpm
    roll_bars = cfg.backtest.walk_forward_roll_months * bpm

    data = DataLayer(cfg)
    df = data.get_ohlcv_history(symbol, tf, bars=total_bars, validate=False)
    funding_history = data.get_funding_history(symbol, limit=500)
    oi_full = data.get_oi_history(symbol, tf, limit=500)

    oos_trades: list[TradeRecord] = []
    is_trades: list[TradeRecord] = []
    folds = 0
    start = 0

    while start + train_bars + val_bars <= len(df) and folds < cfg.backtest.walk_forward_min_folds + 10:
        val_start = start + train_bars
        val_end = val_start + val_bars
        is_result = run_backtest(
            symbol, tf, months=1, config=cfg,
            start_bar=start, end_bar=val_start,
            df=df, funding_history=funding_history, oi_full=oi_full,
        )
        oos_result = run_backtest(
            symbol, tf, months=1, config=cfg,
            start_bar=val_start, end_bar=val_end,
            df=df, funding_history=funding_history, oi_full=oi_full,
        )
        is_trades.extend(is_result.trades)
        oos_trades.extend(oos_result.trades)
        folds += 1
        start += roll_bars
        if folds >= cfg.backtest.walk_forward_min_folds and start + train_bars + val_bars > len(df):
            break

    is_stats = bucket_stats_from_trades(is_trades)
    oos_stats = bucket_stats_from_trades(oos_trades)

    is_pf = _aggregate_pf(is_trades)
    oos_pf = _aggregate_pf(oos_trades)
    accepted = oos_pf >= cfg.backtest.oos_pf_ratio_min * is_pf if is_pf > 0 else bool(oos_trades)

    return {
        "folds": folds,
        "in_sample_trades": len(is_trades),
        "out_of_sample_trades": len(oos_trades),
        "in_sample_stats": is_stats,
        "out_of_sample_stats": oos_stats,
        "in_sample_profit_factor": is_pf,
        "out_of_sample_profit_factor": oos_pf,
        "accepted": accepted,
        "oos_trades": oos_trades,
    }


def _aggregate_pf(trades: list[TradeRecord]) -> float:
    gross_profit = sum(t.pnl_r for t in trades if t.pnl_r > 0)
    gross_loss = abs(sum(t.pnl_r for t in trades if t.pnl_r < 0))
    return gross_profit / gross_loss if gross_loss else float("inf")


def save_calibration_data(results: list[BacktestResult], path: Path) -> dict:
    all_trades: list[TradeRecord] = []
    for result in results:
        all_trades.extend(result.trades)
    stats = bucket_stats_from_trades(all_trades)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(stats, indent=2))
    return stats


def no_lookahead_score(df: pd.DataFrame, bar_index: int, config: EngineConfig | None = None) -> float:
    """Shift test: score at bar_index must not depend on future bars."""
    cfg = config or load_config()
    window = df.iloc[: bar_index + 1].copy()
    return analyze_technical(window, window, cfg).score
