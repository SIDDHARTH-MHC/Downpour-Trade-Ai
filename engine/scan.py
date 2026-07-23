"""Parallel pair scanning (§12.1)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

from engine.analyzer import analyze_symbol
from engine.config import EngineConfig, load_config
from engine.data import DataLayer
from engine.models import Verdict


def scan_pairs(
    symbols: list[str],
    tf: str = "1h",
    *,
    config: EngineConfig | None = None,
    max_workers: int = 5,
    light: bool = True,
    actionable_only: bool = False,
) -> list[Verdict]:
    """Scan pairs concurrently with shared data layer cache."""
    cfg = config or load_config()
    data = DataLayer(cfg)
    # Warm BTC cache once for alt correlation checks
    try:
        data.get_ohlcv("BTC/USDT", "1h", bars=10, validate=False)
    except Exception:
        pass

    results: list[Verdict] = []

    def _analyze(sym: str) -> Verdict | None:
        try:
            return analyze_symbol(sym, tf, light=light, config=cfg)
        except Exception:
            return None

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_analyze, sym): sym for sym in symbols}
        for fut in as_completed(futures):
            verdict = fut.result()
            if verdict is None:
                continue
            if actionable_only and verdict.action == "NO_TRADE":
                continue
            results.append(verdict)

    results.sort(key=lambda v: abs(v.weighted_score), reverse=True)
    return results
