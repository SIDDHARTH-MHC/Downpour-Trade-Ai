from api.coach import coach_reply
from engine.portfolio_analytics import portfolio_analytics


def test_coach_no_trading_advice():
    r = coach_reply("should I buy btc now?", {})
    assert "not trading advice" in r["markdown"].lower() or "does not" in r["markdown"].lower()


def test_portfolio_heat():
    positions = [
        {
            "payload": {
                "symbol": "ETH/USDT",
                "action": "LONG",
                "trade_plan": {"reward_risk": 2.0, "entry": 1, "stop_loss": 0.9, "tp1": 1.2},
            }
        }
    ]
    stats = portfolio_analytics(positions, equity_usd=10_000)
    assert stats["open_trades"] == 1
    assert stats["portfolio_heat_pct"] == 1.0
