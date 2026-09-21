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


class ExecutionClass(str, Enum):
    APP_NATIVE = "app-native"
    PINNED_RUNTIME_RELEASE = "pinned-runtime-release"
    DEDICATED_RUNTIME_CHECKOUT = "dedicated-runtime-checkout"
    DEVELOPMENT_WORKTREE_ONLY = "development-worktree-only"


@dataclass(frozen=True)
class AutomationDefinitionBinding:
    """Immutable declaration; it does not claim provider-native state."""

    automation_id: str
    definition_version: int
    automation_payload_hash: str
    definition_source: str
    definition_branch: str
    definition_commit: str | None
    definition_content_hash: str | None
    owner_ref: str
    provider_ref: str
    execution_class: ExecutionClass
    execution_pin: str | None = None

    def validate(self) -> None:
        _nonempty(self.automation_id, "automation_id")
        if (
            isinstance(self.definition_version, bool)
            or not isinstance(self.definition_version, int)
            or self.definition_version < 1
        ):
            raise ValueError("definition_version must be a positive integer")
        _sha256(self.automation_payload_hash, "automation_payload_hash")
        _repo_uri(self.definition_source)
        _branch(self.definition_branch)
        if self.definition_commit is None and self.definition_content_hash is None:
            raise ValueError("definition source requires immutable commit or content hash")
        if self.definition_commit is not None:
            _git_commit(self.definition_commit)
        if self.definition_content_hash is not None:
            _sha256(self.definition_content_hash, "definition_content_hash")
        _typed_ref(self.owner_ref, "owner_ref")
        _typed_ref(self.provider_ref, "provider_ref")
        if not isinstance(self.execution_class, ExecutionClass):
            raise ValueError("execution_class must use the native enum")
        if self.execution_class != ExecutionClass.APP_NATIVE and self.execution_pin is None:
            raise ValueError("non-app-native bindings require execution_pin")
        if self.execution_pin is not None:
            _execution_pin(self.execution_pin)

    def as_payload(self) -> dict[str, Any]:
        self.validate()
        return {
            "schema": "automation-definition-binding.v1",
            "automation_id": self.automation_id,
            "definition_version": self.definition_version,
            "automation_payload_hash": self.automation_payload_hash,
            "definition_source": self.definition_source,
            "definition_branch": self.definition_branch,
            "definition_commit": self.definition_commit,
            "definition_content_hash": self.definition_content_hash,
            "owner_ref": self.owner_ref,
            "provider_ref": self.provider_ref,
            "execution_class": self.execution_class.value,
            "execution_pin": self.execution_pin,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> AutomationDefinitionBinding:
        required = {
            "schema",
            "automation_id",
            "definition_version",
            "automation_payload_hash",
            "definition_source",
            "definition_branch",
            "definition_commit",
            "definition_content_hash",
            "owner_ref",
            "provider_ref",
            "execution_class",
            "execution_pin",
        }
        if set(payload) != required or payload.get("schema") != "automation-definition-binding.v1":
            raise ValueError("invalid automation definition binding payload")
        try:
            result = cls(
                automation_id=payload["automation_id"],
                definition_version=payload["definition_version"],
                automation_payload_hash=payload["automation_payload_hash"],
                definition_source=payload["definition_source"],
                definition_branch=payload["definition_branch"],
                definition_commit=payload["definition_commit"],
                definition_content_hash=payload["definition_content_hash"],
                owner_ref=payload["owner_ref"],
                provider_ref=payload["provider_ref"],
                execution_class=ExecutionClass(payload["execution_class"]),
                execution_pin=payload["execution_pin"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid automation definition binding payload") from exc
        result.validate()
        return result


def _nonempty(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _sha256(value: Any, name: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(f"{name} must be a lowercase sha256")


def _git_commit(value: Any) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 40
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError("definition_commit must be a lowercase git commit")


def _execution_pin(value: Any) -> None:
    if not isinstance(value, str):
        raise ValueError("execution_pin must be immutable")
    raw = value.removeprefix("sha256:")
    if len(raw) not in {40, 64} or any(char not in "0123456789abcdef" for char in raw):
        raise ValueError("execution_pin must be immutable")
    if value.startswith("sha256:") and len(raw) != 64:
        raise ValueError("execution_pin must be immutable")


def _branch(value: Any) -> None:
    _nonempty(value, "definition_branch")
    if (
        any(char.isspace() or ord(char) < 32 for char in value)
        or any(char in value for char in "~^:?*[]\\")
        or value.startswith(("/", "."))
        or value.endswith("/")
        or ".." in value
    ):
        raise ValueError("definition_branch is unsafe")


def _repo_uri(value: Any) -> None:
    _nonempty(value, "definition_source")
    if (
        not value.startswith("repo://")
        or any(char.isspace() or ord(char) < 32 for char in value)
        or any(char in value for char in "@?#\\")
    ):
        raise ValueError("definition_source must be a credential-free repo URI")
    remainder = value[len("repo://") :]
    if "/" not in remainder or any(not segment for segment in remainder.split("/")):
        raise ValueError("definition_source must identify a repository")


def _typed_ref(value: Any, name: str) -> None:
    _nonempty(value, name)
    if any(char.isspace() or ord(char) < 32 for char in value) or any(
        char in value for char in "@/?#\\"
    ):
        raise ValueError(f"{name} is unsafe")
    prefix, separator, identifier = value.partition(":")
    if (
        separator != ":"
        or not prefix
        or not identifier
        or not prefix.replace("-", "").replace("_", "").isalnum()
        or not identifier.replace("-", "").replace("_", "").replace(".", "").isalnum()
    ):
        raise ValueError(f"{name} must be a typed reference")



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

