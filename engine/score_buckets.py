"""Shared score buckets for backtests, confidence labels, and trust card."""


def score_bucket(score: float, action: str) -> str:
    """
    Map weighted synthesizer score + action to calibration bucket keys.

    LONG uses signed score; SHORT uses magnitude (negative scores bucket like positive SHORT bias).
    """
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
