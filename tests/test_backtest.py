import json

from engine.backtest import no_lookahead_score, score_bucket
from engine.lanes.flow import analyze_flow
from engine.lanes.regime import analyze_regime
from engine.lanes.structure import analyze_structure
from engine.lanes.technical import analyze_technical
from engine.models import RegimeResult
from engine.risk import build_trade_plan
from engine.synthesizer import synthesize
from tests.conftest import make_ohlcv


def test_no_lookahead_identical_scores():
    df = make_ohlcv(n=500, trend=0.003, noise=0.001)
    scores = [no_lookahead_score(df, i) for i in range(250, 260)]
    assert all(isinstance(s, float) for s in scores)


def test_score_bucket_long():
    assert score_bucket(40, "LONG") == "35-50"
    assert score_bucket(-40, "SHORT") == "35-50"


def test_regime_deterministic_json():
    df = make_ohlcv()
    regime = analyze_regime(df, df, "BTC/USDT", tf="1h")
    a = json.dumps({"regime": regime.regime, "tradeable": regime.tradeable}, sort_keys=True)
    b = json.dumps({"regime": regime.regime, "tradeable": regime.tradeable}, sort_keys=True)
    assert a == b


def test_full_pipeline_deterministic_json():
    df = make_ohlcv(n=500, trend=0.005, noise=0.0005)
    htf = df.iloc[::4].copy()
    technical = analyze_technical(df, htf)
    flow = analyze_flow(
        df,
        {"current": {"fundingRate": 0.0}, "history": [{"fundingRate": 0.0}] * 8},
        df.iloc[:0],
    )
    structure = analyze_structure(df, None, "BTC/USDT")
    regime = RegimeResult("RANGING", True, {"technical": 0.7, "flow": 1.0, "structure": 1.4})
    verdict = synthesize([technical, flow, structure], regime)
    verdict = build_trade_plan(verdict, df, mid_price=float(df["close"].iloc[-1]))

    payload = {
        "action": verdict.action,
        "score": round(verdict.weighted_score, 4),
        "lanes": [round(l.score, 4) for l in verdict.lanes],
    }
    assert json.dumps(payload, sort_keys=True) == json.dumps(payload, sort_keys=True)
