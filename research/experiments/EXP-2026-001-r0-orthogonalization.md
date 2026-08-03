# EXP-2026-001: R0 technical orthogonalization

**Status:** Implemented (production defaults = **T3**) — walk-forward sign-off pending  
**Baseline:** B0 via `research/variants.py`  
**Owner:** Technical lane  

## Hypothesis

Reducing correlated trend/momentum terms improves OOS stability.

## Variants

| ID | Config |
|----|--------|
| B0 | Legacy: full EMA200 side, MACD independent, ADX on full score |
| T1 | EMA200 only when stack neutral |
| T2 | T1 + MACD requires stack agreement |
| T3 | T2 + ADX on trend sub-score only (**production default**) |

## Run

```bash
python cli.py research walk-forward --compare --months 12 --symbols BTC/USDT,ETH/USDT,SOL/USDT
```

## Decision

- [x] P4 Lane score (T3 defaults in `config.yaml`)
- [ ] Walk-forward sign-off recorded below

## Results

| Variant | Symbol | OOS PF | OOS trades | WF pass |
|---------|--------|--------|------------|---------|
| _fill after run_ | | | | |

## Integration

- `engine/lanes/technical.py`
- `engine/config.py` + `config.yaml`
- `engine/config_hash.py` on verdicts
- `research/runner.py`, `cli.py research walk-forward`

## Rollback

Set in `config.yaml`:

```yaml
ema200_side_only_when_stack_neutral: false
macd_requires_stack_agreement: false
adx_multiplier_scope: full
```
