from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class LaneResult:
    name: str
    score: float
    evidence: list[str]
    values: dict[str, float]
    no_edge: bool = False


@dataclass
class RegimeResult:
    regime: str
    tradeable: bool
    lane_weights: dict[str, float]
    evidence: list[str] = field(default_factory=list)
    values: dict[str, float] = field(default_factory=dict)


@dataclass
class Explanation:
    decision: str
    why: list[str]
    why_not: list[str]
    risk: list[str]


@dataclass
class TradePlan:
    entry: float
    stop_loss: float
    tp1: float
    tp2: float
    reward_risk: float
    size_coin: float
    size_usd: float
    patient: bool = False


@dataclass
class Verdict:
    action: str
    weighted_score: float
    lanes: list[LaneResult]
    regime: RegimeResult
    confidence: str
    trade_plan: TradePlan | None
    reasons: list[str]
    explanation: Explanation | None = None
    symbol: str = ""
    timeframe: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "app": "Downpour Trade AI",
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp,
            "action": self.action,
            "weighted_score": round(self.weighted_score, 2),
            "confidence": self.confidence,
            "regime": {
                "name": self.regime.regime,
                "tradeable": self.regime.tradeable,
                "lane_weights": self.regime.lane_weights,
                "evidence": self.regime.evidence,
            },
            "lanes": [
                {
                    "name": lane.name,
                    "score": round(lane.score, 2),
                    "evidence": lane.evidence,
                    "values": {k: round(v, 6) if isinstance(v, float) else v for k, v in lane.values.items()},
                    "no_edge": lane.no_edge,
                }
                for lane in self.lanes
            ],
            "reasons": self.reasons,
            "explanation": None if self.explanation is None else {
                "decision": self.explanation.decision,
                "why": self.explanation.why,
                "why_not": self.explanation.why_not,
                "risk": self.explanation.risk,
            },
            "trade_plan": None
            if self.trade_plan is None
            else {
                "entry": round(self.trade_plan.entry, 4),
                "stop_loss": round(self.trade_plan.stop_loss, 4),
                "tp1": round(self.trade_plan.tp1, 4),
                "tp2": round(self.trade_plan.tp2, 4),
                "reward_risk": round(self.trade_plan.reward_risk, 2),
                "size_coin": round(self.trade_plan.size_coin, 6),
                "size_usd": round(self.trade_plan.size_usd, 2),
                "patient": self.trade_plan.patient,
            },
        }
