from engine.lifecycle import lifecycle_state
from engine.replay import build_replay_events


def test_replay_events_order():
    payload = {
        "action": "LONG",
        "weighted_score": 42,
        "regime": {"evidence": ["regime ok"]},
        "lanes": [{"name": "technical", "evidence": ["ema bull"], "score": 40}],
        "reasons": ["aligned"],
        "explanation": {"why": ["because"], "why_not": [], "risk": []},
    }
    events = build_replay_events(payload)
    assert len(events) >= 3
    assert events[0]["category"] == "regime"


def test_lifecycle_open_long():
    payload = {"action": "LONG", "trade_plan": {"patient": False, "entry": 1, "stop_loss": 0.9, "tp1": 1.1}}
    state = lifecycle_state(payload, None)
    assert state["stage"] in {"confirmed", "waiting", "detected"}
