import pandas as pd

from engine.calibration import calibrate_label
from engine.models import LaneResult, RegimeResult, Verdict
from engine.outcomes import resolve_outcome_after_signal, verdict_bar_timestamp_ms
from engine.score_buckets import score_bucket


def test_score_bucket_matches_trust_and_calibration():
    assert score_bucket(55, "LONG") == "50+"
    assert score_bucket(40, "LONG") == "35-50"
    assert score_bucket(10, "LONG") == "neutral"
    assert score_bucket(-45, "SHORT") == "35-50"
    assert score_bucket(-55, "SHORT") == "50+"


def test_calibrate_label_uses_same_bucket_as_score_bucket():
    tables = {
        "35-50": {"trade_count": 120, "win_rate": 0.56, "profit_factor": 1.5},
    }
    verdict = Verdict(
        action="LONG",
        weighted_score=42.0,
        lanes=[LaneResult("technical", 40, [], {})],
        regime=RegimeResult("RANGING", True, {}, [], {}),
        confidence="",
        trade_plan=None,
        reasons=[],
    )
    label = calibrate_label(verdict, tables=tables)
    assert "HIGH" in label or "MODERATE" in label or "LOW" in label
    assert score_bucket(verdict.weighted_score, verdict.action) == "35-50"


def test_verdict_bar_timestamp_ms():
    ms = verdict_bar_timestamp_ms({"timestamp": "2026-08-03 19:00 UTC"})
    assert ms is not None
    assert ms > 1_700_000_000_000


def test_outcome_only_after_signal_bar():
    df = pd.DataFrame(
        [
            {"timestamp": 1000, "high": 110, "low": 90},
            {"timestamp": 2000, "high": 105, "low": 95},
            {"timestamp": 3000, "high": 108, "low": 88},
        ]
    )
    assert (
        resolve_outcome_after_signal(
            df, action="LONG", stop_loss=92, tp1=120, signal_bar_ms=1000
        )
        == "SL"
    )
    df2 = pd.DataFrame([{"timestamp": 1000, "high": 110, "low": 90}])
    assert (
        resolve_outcome_after_signal(
            df2, action="LONG", stop_loss=92, tp1=120, signal_bar_ms=1000
        )
        is None
    )
