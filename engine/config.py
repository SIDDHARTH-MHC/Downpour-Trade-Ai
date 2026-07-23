from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class DataConfig(BaseModel):
    cache_dir: str = "./data"
    ohlcv_bars: int = 500
    retry_attempts: int = 3
    retry_base_delay_sec: float = 1.0
    staleness_multiplier: float = 2.0


class TechnicalConfig(BaseModel):
    ema_stack_bull: float = 25
    ema_stack_bear: float = -25
    ema200_side: float = 10
    rsi_bull: float = 10
    rsi_bear: float = -10
    rsi_overbought_penalty: float = -10
    rsi_oversold_penalty: float = 10
    rsi_overbought_threshold: float = 75
    rsi_oversold_threshold: float = 25
    rsi_bull_threshold: float = 60
    rsi_bear_threshold: float = 40
    macd_bull: float = 15
    macd_bear: float = -15
    adx_trend_threshold: float = 25
    adx_trend_multiplier: float = 1.25
    adx_chop_threshold: float = 20
    adx_chop_multiplier: float = 0.6
    htf_multiplier: int = 4


class FlowConfig(BaseModel):
    funding_short_crowd: float = 15
    funding_long_crowd: float = -15
    funding_neutral_low: float = -0.0001
    funding_neutral_high: float = 0.0001
    funding_crowd_long: float = 0.0003
    funding_trend: float = 10
    oi_price_new_longs: float = 15
    oi_price_new_shorts: float = -15
    oi_price_short_cover: float = -5
    oi_price_long_flush: float = 5
    oi_spike_threshold: float = 0.08
    oi_spike_multiplier: float = 1.5
    taker_bull: float = 10
    taker_bear: float = -10
    taker_bull_ratio: float = 0.58
    taker_bear_ratio: float = 0.42
    raw_scale: float = 1.5
    funding_zscore_bull: float = 15
    funding_zscore_bear: float = -15
    funding_zscore_threshold: float = 2.0
    funding_zscore_min_samples: int = 10


class StructureConfig(BaseModel):
    swing_fractal: int = 5
    cluster_atr_factor: float = 0.25
    max_levels: int = 6
    wall_bucket_pct: float = 0.001
    wall_median_multiplier: float = 6
    wall_min_notional_btc_eth: float = 1_000_000
    wall_min_notional_alt: float = 250_000
    support_near_atr: float = 0.5
    resistance_near_atr: float = 0.5
    range_no_edge_atr: float = 1.5
    support_score: float = 20
    resistance_score: float = -20
    breakout_score: float = 25
    breakdown_score: float = -25
    bid_ask_ratio_bull: float = 10
    bid_ask_ratio_bear: float = -10
    bid_ask_ratio_high: float = 2.0
    bid_ask_ratio_low: float = 0.5
    wall_max_contribution: float = 30
    min_touch_breakout: int = 3
    vp_bins: int = 100
    vp_hvn_percentile: float = 70
    vp_lvn_percentile: float = 20
    vp_poc_above_score: float = 10
    vp_poc_below_score: float = -10
    vp_clean_air_score: float = 5


class RegimeConfig(BaseModel):
    shock_percentile: float = 90
    compression_percentile: float = 20
    lookback_days: int = 90
    btc_move_threshold: float = 0.02
    weights: dict[str, dict[str, float]] = Field(default_factory=dict)


class SynthesizerConfig(BaseModel):
    long_threshold: float = 35
    short_threshold: float = -35
    lane_alignment_threshold: float = 20
    min_aligned_lanes: int = 2
    max_adverse_lane: float = -25
    min_adverse_lane_short: float = 25
    lane_conflict_threshold: float = 80


class RiskConfig(BaseModel):
    account_risk_pct: float = 0.01
    default_equity_usd: float = 10_000
    atr_sl_multiplier: float = 1.5
    support_sl_buffer_atr: float = 0.25
    min_reward_risk: float = 1.2
    tp2_rr_multiplier: float = 2.0
    trade_timeout_bars: int = 48


class BacktestConfig(BaseModel):
    fee_pct: float = 0.001
    slippage_pct: float = 0.0005
    default_months: int = 12
    walk_forward_train_months: int = 6
    walk_forward_val_months: int = 2
    walk_forward_roll_months: int = 2
    walk_forward_min_folds: int = 4
    oos_pf_ratio_min: float = 0.7


class CalibrationConfig(BaseModel):
    high_win_rate: float = 0.55
    high_min_trades: int = 100
    high_profit_factor: float = 1.4
    moderate_win_rate: float = 0.48
    moderate_min_trades: int = 50
    moderate_profit_factor: float = 1.15
    insufficient_data_trades: int = 50


class PairsConfig(BaseModel):
    default: str = "BTC/USDT"
    scan_top: int = 20


class EngineConfig(BaseModel):
    app_name: str = "Downpour Trade AI"
    data: DataConfig = Field(default_factory=DataConfig)
    technical: TechnicalConfig = Field(default_factory=TechnicalConfig)
    flow: FlowConfig = Field(default_factory=FlowConfig)
    structure: StructureConfig = Field(default_factory=StructureConfig)
    regime: RegimeConfig = Field(default_factory=RegimeConfig)
    synthesizer: SynthesizerConfig = Field(default_factory=SynthesizerConfig)
    risk: RiskConfig = Field(default_factory=RiskConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    calibration: CalibrationConfig = Field(default_factory=CalibrationConfig)
    pairs: PairsConfig = Field(default_factory=PairsConfig)


def load_config(path: str | Path | None = None) -> EngineConfig:
    config_path = Path(path or "config.yaml")
    if not config_path.exists():
        return EngineConfig()
    with config_path.open() as f:
        raw: dict[str, Any] = yaml.safe_load(f) or {}
    return EngineConfig.model_validate(raw)
