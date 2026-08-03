"""Research experiment utilities (walk-forward comparison)."""

from __future__ import annotations

from typing import Any

from engine.config import EngineConfig, TechnicalConfig, load_config

# Research_Roadmap.md EXP-R0 variants
R0_VARIANTS: dict[str, dict[str, Any]] = {
    "B0": {
        "ema200_side_only_when_stack_neutral": False,
        "macd_requires_stack_agreement": False,
        "adx_multiplier_scope": "full",
    },
    "T1": {
        "ema200_side_only_when_stack_neutral": True,
        "macd_requires_stack_agreement": False,
        "adx_multiplier_scope": "full",
    },
    "T2": {
        "ema200_side_only_when_stack_neutral": True,
        "macd_requires_stack_agreement": True,
        "adx_multiplier_scope": "full",
    },
    "T3": {
        "ema200_side_only_when_stack_neutral": True,
        "macd_requires_stack_agreement": True,
        "adx_multiplier_scope": "trend_subscore",
    },
}


def config_for_variant(variant: str, config_path: str | None = None) -> EngineConfig:
    key = variant.upper()
    if key not in R0_VARIANTS:
        raise ValueError(f"Unknown variant {variant!r}; choose from {list(R0_VARIANTS)}")
    base = load_config(config_path)
    tech = base.technical.model_copy(update=R0_VARIANTS[key])
    return base.model_copy(update={"technical": tech})


def production_r0_config(config_path: str | None = None) -> EngineConfig:
    """Current production defaults (T3-equivalent orthogonalization)."""
    return config_for_variant("T3", config_path)
