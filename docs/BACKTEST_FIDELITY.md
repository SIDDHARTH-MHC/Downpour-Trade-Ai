# Backtest & calibration fidelity

Live `/analyze` and scheduled **scan** use more market data than historical **backtests** and **walk-forward calibration**. That is intentional for MVP performance, but confidence labels must be interpreted with these limits.

## Live vs backtest

| Input | Live analyze | Backtest / walk-forward |
|--------|----------------|-------------------------|
| OHLCV | Yes | Yes (no lookahead: `df.iloc[:i+1]`) |
| Order book / walls | Yes | **No** (`book=None`, `structure_degraded=True`) |
| Taker trade imbalance | Yes (unless `light=True`) | **No** (`trades=[]`) |
| Funding + OI | Yes | Yes when history exists at bar time; else flow lane skipped |
| Regime / technical | Yes | Yes |

**Implication:** Structure and flow scores in production can be **stronger or different** than in OOS calibration. Trust Card stats describe **degraded-mode backtests**, not a pixel-perfect replay of live lane scores.

## Confidence buckets

- Buckets are defined in `engine/score_buckets.py` (`50+`, `35-50`, signed shorts, `neutral`).
- **Trust Card**, **calibrate_label**, and **backtest** all use the same function.
- Labels (HIGH / MODERATE / LOW) come from OOS walk-forward trades binned into those keys.

## Walk-forward

- Train/validation folds: see `config.yaml` → `backtest.walk_forward_*`.
- Acceptance: OOS profit factor vs IS ratio (`oos_pf_ratio_min`).
- Re-run calibration monthly or after config changes (`POST /calibrate` or scheduler weekly job).

## Outcome tracking (live history)

- Open LONG/SHORT outcomes are resolved from OHLCV **only on bars after the signal candle** (`engine/outcomes.py`).
- Same-bar TP/SL after signal close are excluded to avoid look-ahead in win-rate / confidence-history stats.

## When comparing live to backtest

1. Expect **fewer** structure-driven edges in calibration than in live scans.
2. Treat **INSUFFICIENT_DATA** as normal until enough OOS trades fill a bucket.
3. Do not expect live win rate to match bucket win rate without periodic re-calibration.
