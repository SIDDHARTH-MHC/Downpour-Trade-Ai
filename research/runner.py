"""Run walk-forward experiments (Research_Roadmap.md)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from engine.backtest import run_walk_forward
from engine.config_hash import config_hash
from research.variants import R0_VARIANTS, config_for_variant


@dataclass
class WfExperimentResult:
    variant: str
    symbol: str
    months: int
    config_hash: str
    folds: int
    in_sample_trades: int
    out_of_sample_trades: int
    in_sample_profit_factor: float
    out_of_sample_profit_factor: float
    accepted: bool

    def to_dict(self) -> dict:
        return {
            "variant": self.variant,
            "symbol": self.symbol,
            "months": self.months,
            "config_hash": self.config_hash,
            "folds": self.folds,
            "in_sample_trades": self.in_sample_trades,
            "out_of_sample_trades": self.out_of_sample_trades,
            "in_sample_profit_factor": round(self.in_sample_profit_factor, 4),
            "out_of_sample_profit_factor": round(self.out_of_sample_profit_factor, 4),
            "accepted": self.accepted,
        }


def run_r0_walk_forward(
    variant: str,
    symbol: str,
    months: int = 12,
    *,
    config_path: str | None = None,
) -> WfExperimentResult:
    cfg = config_for_variant(variant, config_path)
    wf = run_walk_forward(symbol, "1h", months, cfg)
    return WfExperimentResult(
        variant=variant.upper(),
        symbol=symbol,
        months=months,
        config_hash=config_hash(cfg),
        folds=int(wf.get("folds", 0)),
        in_sample_trades=int(wf.get("in_sample_trades", 0)),
        out_of_sample_trades=int(wf.get("out_of_sample_trades", 0)),
        in_sample_profit_factor=float(wf.get("in_sample_profit_factor", 0)),
        out_of_sample_profit_factor=float(wf.get("out_of_sample_profit_factor", 0)),
        accepted=bool(wf.get("accepted")),
    )


def compare_r0_variants(
    symbols: list[str],
    months: int = 12,
    variants: list[str] | None = None,
    *,
    config_path: str | None = None,
) -> list[WfExperimentResult]:
    keys = [v.upper() for v in (variants or list(R0_VARIANTS))]
    results: list[WfExperimentResult] = []
    for sym in symbols:
        for var in keys:
            results.append(run_r0_walk_forward(var, sym, months, config_path=config_path))
    return results


def write_results_json(results: list[WfExperimentResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([r.to_dict() for r in results], indent=2))
