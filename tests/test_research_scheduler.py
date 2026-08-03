import pytest

from research_platform.promotion_guard import assert_manual_promotion_only, validate_promotion_decision


def test_scheduler_cannot_promote():
    with pytest.raises(RuntimeError, match="Scheduler cannot"):
        validate_promotion_decision("PROMOTED", source="scheduler")


def test_manual_context_allowed():
    assert_manual_promotion_only(context="manual_review")
