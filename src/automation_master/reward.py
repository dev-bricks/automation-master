"""Deterministic, explainable reward calculation.

The defaults are conservative implementation defaults, not a claim that the
domain weights have already been approved. Deployments can version and replace
them through policy events.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .models import RewardSignals


@dataclass(frozen=True)
class RewardResult:
    score: float
    proposed_credits: int
    components: dict[str, float]
    explanation: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RewardPolicy:
    """Configurable reward policy with bounded movement and exploration."""

    positive_weights: dict[str, float] = field(
        default_factory=lambda: {
            "current_interest": 22.0,
            "coverage_gap": 24.0,
            "deadline_pressure": 16.0,
            "utility": 28.0,
            "independent_review_value": 10.0,
        }
    )
    negative_weights: dict[str, float] = field(
        default_factory=lambda: {
            "cost_per_useful_result": 18.0,
            "no_work_rate": 20.0,
            "error_rate": 26.0,
            "redundancy": 16.0,
        }
    )
    score_floor: float = 0.0
    score_cap: float = 100.0
    exploration_floor: float = 5.0
    decay_per_stale_epoch: float = 0.92
    hysteresis_threshold: float = 3.0
    max_change_per_epoch: float = 15.0
    min_credits: int = 0
    max_credits: int = 20

    def validate(self) -> None:
        if not 0 <= self.score_floor <= self.exploration_floor <= self.score_cap:
            raise ValueError("score bounds are inconsistent")
        if not 0 < self.decay_per_stale_epoch <= 1:
            raise ValueError("decay_per_stale_epoch must be in (0, 1]")
        if self.hysteresis_threshold < 0 or self.max_change_per_epoch < 0:
            raise ValueError("hysteresis values must be non-negative")
        if not 0 <= self.min_credits <= self.max_credits:
            raise ValueError("credit bounds are inconsistent")

    def score(
        self,
        signals: RewardSignals,
        *,
        previous_score: float | None = None,
    ) -> RewardResult:
        self.validate()
        signals.validate()
        values = asdict(signals)
        components: dict[str, float] = {}
        for name, weight in self.positive_weights.items():
            components[name] = round(float(values[name]) * weight, 6)
        for name, weight in self.negative_weights.items():
            components[name] = round(-float(values[name]) * weight, 6)

        raw = sum(components.values())
        decayed = raw * (self.decay_per_stale_epoch ** signals.stale_epochs)
        bounded = min(self.score_cap, max(self.score_floor, decayed))
        if bounded > self.score_floor:
            bounded = max(self.exploration_floor, bounded)

        hysteresis = "initial"
        if previous_score is not None:
            previous = min(self.score_cap, max(self.score_floor, previous_score))
            delta = bounded - previous
            if abs(delta) < self.hysteresis_threshold:
                bounded = previous
                hysteresis = "held"
            elif abs(delta) > self.max_change_per_epoch:
                bounded = previous + (
                    self.max_change_per_epoch if delta > 0 else -self.max_change_per_epoch
                )
                hysteresis = "step-capped"
            else:
                hysteresis = "moved"

        bounded = round(min(self.score_cap, max(self.score_floor, bounded)), 6)
        span = self.max_credits - self.min_credits
        proposed = self.min_credits + round((bounded / self.score_cap) * span)
        proposed = min(self.max_credits, max(self.min_credits, proposed))
        explanation = (
            f"raw={raw:.3f}; stale_epochs={signals.stale_epochs}; "
            f"decayed={decayed:.3f}; hysteresis={hysteresis}; bounded={bounded:.3f}"
        )
        return RewardResult(bounded, proposed, components, explanation)
