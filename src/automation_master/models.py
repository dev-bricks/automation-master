"""Domain types shared by the registry, ledger, and adapters."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def content_hash(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def new_event_id() -> str:
    return str(uuid.uuid4())


class MutationClass(str, Enum):
    READ_ONLY_REDUNDANT = "read-only-redundant"
    INDEPENDENT_REVIEW = "independent-review"
    SINGLE_WRITER_PER_SLOT = "single-writer-per-slot"
    GLOBALLY_SINGLE_WRITER = "globally-single-writer"


class RunClass(str, Enum):
    COMPARABLE = "comparable"
    UNIQUE = "unique"
    SAFETY = "safety"
    DEADLINE = "deadline"


class EnforcementMode(str, Enum):
    DISABLED = "disabled"
    SHADOW = "shadow"
    ENFORCED = "enforced"


@dataclass(frozen=True)
class AutomationSpec:
    automation_id: str
    family_id: str
    variant_id: str
    mutation_class: MutationClass
    run_class: RunClass = RunClass.COMPARABLE
    version: int = 1
    enabled: bool = True

    def as_payload(self) -> dict[str, Any]:
        result = asdict(self)
        result["mutation_class"] = self.mutation_class.value
        result["run_class"] = self.run_class.value
        return result


@dataclass(frozen=True)
class RewardSignals:
    current_interest: float = 0.0
    coverage_gap: float = 0.0
    deadline_pressure: float = 0.0
    utility: float = 0.0
    cost_per_useful_result: float = 0.0
    no_work_rate: float = 0.0
    error_rate: float = 0.0
    redundancy: float = 0.0
    independent_review_value: float = 0.0
    stale_epochs: int = 0

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if name == "stale_epochs":
                if value < 0:
                    raise ValueError("stale_epochs must be non-negative")
            elif not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class ReservationDecision:
    status: str
    run_id: str
    reservation_id: str | None
    credits: int
    available_before: int
    explanation: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

