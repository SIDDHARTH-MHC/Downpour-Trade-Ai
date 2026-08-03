from engine.scenario import simulate_shock


def test_scenario_btc_long_sl_on_crash():
    positions = [
        {
            "symbol": "BTC/USDT",
            "action": "LONG",
            "trade_plan": {"entry": 100.0, "stop_loss": 95.0, "tp1": 110.0},
        }
    ]
    out = simulate_shock(positions, shock_pct=-0.10, shock_asset="BTC")
    assert out["positions"][0]["sl_hit"] is True
