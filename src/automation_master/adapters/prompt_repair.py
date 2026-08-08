"""Fail-closed contract verifier for provider prompt-repair adapters.

This module deliberately does **not** open, edit, replace, validate, or
activate a provider configuration.  It verifies a provider adapter's proposed
before/after transaction in memory, so an Antigravity-style self-healing
adapter can be tested before any mutation authority is granted.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from ..models import content_hash
from ..security import contains_sensitive_text

INVARIANT_FIELDS = (
    "model",
    "thinking",
    "schedule",
    "enabled",
    "status",
    "target",
    "cwd",
)
RECEIPT_FIELDS = (
    "provider",
    "automation_id",
    "before_hash",
    "after_hash",
    "backup_hash",
    "validation",
    "rollback",
    "diff_summary",
)


class PromptRepairContractError(ValueError):
    """The proposed provider transaction violates the repair contract."""


@dataclass(frozen=True)
class PromptRepairContractResult:
    """Auditable result of a pure in-memory contract verification."""

    ok: bool
    errors: tuple[str, ...]
    before_hash: str
    after_hash: str
    backup_hash: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "errors": list(self.errors),
            "before_hash": self.before_hash,
            "after_hash": self.after_hash,
            "backup_hash": self.backup_hash,
        }


class PromptRepairContractAdapter:
    """Verify a prompt-only provider repair without performing the repair."""

    provider = "generic"

    def verify(
        self,
        *,
        before: Mapping[str, Any],
        after: Mapping[str, Any],
        original_bytes: bytes,
        backup_bytes: bytes,
        requested_prompt: str,
        receipt: Mapping[str, Any],
    ) -> PromptRepairContractResult:
        before_hash = content_hash(dict(before))
        after_hash = content_hash(dict(after))
        backup_hash = _bytes_hash(backup_bytes)
        errors: list[str] = []

        if backup_bytes != original_bytes:
            errors.append("backup is not byte-exact")
        for field in INVARIANT_FIELDS:
            if field not in before or field not in after:
                errors.append(f"missing invariant field: {field}")
            elif before[field] != after[field]:
                errors.append(f"invariant changed: {field}")

        changed = {
            key
            for key in set(before) | set(after)
            if before.get(key) != after.get(key)
        }
        if changed - {"prompt"}:
            errors.append("change is not limited to prompt")
        if not isinstance(before.get("prompt"), str):
            errors.append("before.prompt must be a string")
        if not isinstance(after.get("prompt"), str):
            errors.append("after.prompt must be a string")
        elif after["prompt"] != requested_prompt:
            errors.append("after.prompt does not match requested prompt")

        errors.extend(self._verify_receipt(receipt, before_hash, after_hash, backup_hash))
        return PromptRepairContractResult(
            ok=not errors,
            errors=tuple(dict.fromkeys(errors)),
            before_hash=before_hash,
            after_hash=after_hash,
            backup_hash=backup_hash,
        )

    def assert_valid(self, **kwargs: Any) -> PromptRepairContractResult:
        result = self.verify(**kwargs)
        if not result.ok:
            raise PromptRepairContractError("; ".join(result.errors))
        return result

    def verify_rollback(
        self,
        *,
        original_bytes: bytes,
        restored_bytes: bytes,
        receipt: Mapping[str, Any],
    ) -> None:
        """Verify the failed-transaction rollback side of the contract."""
        if restored_bytes != original_bytes:
            raise PromptRepairContractError("rollback did not restore original bytes")
        if receipt.get("rollback") is not True:
            raise PromptRepairContractError("rollback receipt flag is not true")

    def _verify_receipt(
        self,
        receipt: Mapping[str, Any],
        before_hash: str,
        after_hash: str,
        backup_hash: str,
    ) -> list[str]:
        errors: list[str] = []
        missing = [field for field in RECEIPT_FIELDS if field not in receipt]
        if missing:
            errors.append(f"receipt fields missing: {', '.join(missing)}")
            return errors
        if receipt.get("provider") != self.provider:
            errors.append("receipt provider mismatch")
        if not str(receipt.get("automation_id") or "").strip():
            errors.append("receipt automation_id is required")
        if receipt.get("before_hash") != before_hash:
            errors.append("receipt before_hash mismatch")
        if receipt.get("after_hash") != after_hash:
            errors.append("receipt after_hash mismatch")
        if receipt.get("backup_hash") != backup_hash:
            errors.append("receipt backup_hash mismatch")
        if receipt.get("validation") is not True:
            errors.append("provider validation was not successful")
        if receipt.get("rollback") is not False:
            errors.append("successful repair must have rollback=false")
        if contains_sensitive_text(receipt.get("diff_summary")):
            errors.append("receipt diff_summary contains sensitive text")
        return errors


class AntigravityPromptRepairContractAdapter(PromptRepairContractAdapter):
    """Named contract seam for an Antigravity-style provider adapter."""

    provider = "antigravity"


def _bytes_hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


__all__ = [
    "INVARIANT_FIELDS",
    "RECEIPT_FIELDS",
    "AntigravityPromptRepairContractAdapter",
    "PromptRepairContractAdapter",
    "PromptRepairContractError",
    "PromptRepairContractResult",
]
