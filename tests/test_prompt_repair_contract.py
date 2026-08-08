from __future__ import annotations

import hashlib

import pytest

from automation_master.adapters.prompt_repair import (
    AntigravityPromptRepairContractAdapter,
    PromptRepairContractError,
)
from automation_master.models import content_hash


def valid_transaction() -> tuple[dict[str, object], dict[str, object], bytes, dict[str, object]]:
    before = {
        "model": "gpt-5.6-sol",
        "thinking": "medium",
        "schedule": "0 * * * *",
        "enabled": True,
        "status": "ready",
        "target": "workstation",
        "cwd": "C:/automation",
        "prompt": "old prompt",
    }
    after = {**before, "prompt": "new prompt"}
    original = b'{"prompt":"old prompt"}\n'
    receipt = {
        "provider": "antigravity",
        "automation_id": "automation-1",
        "before_hash": content_hash(before),
        "after_hash": content_hash(after),
        "backup_hash": hashlib.sha256(original).hexdigest(),
        "validation": True,
        "rollback": False,
        "diff_summary": {"changed_fields": ["prompt"]},
    }
    return before, after, original, receipt


def test_antigravity_contract_accepts_prompt_only_transaction():
    before, after, original, receipt = valid_transaction()
    adapter = AntigravityPromptRepairContractAdapter()

    result = adapter.verify(
        before=before,
        after=after,
        original_bytes=original,
        backup_bytes=original,
        requested_prompt="new prompt",
        receipt=receipt,
    )

    assert result.ok
    assert result.errors == ()
    assert result.as_dict()["ok"] is True


def test_contract_rejects_invariant_mutation_and_non_exact_backup():
    before, after, original, receipt = valid_transaction()
    after["model"] = "different-model"
    adapter = AntigravityPromptRepairContractAdapter()

    result = adapter.verify(
        before=before,
        after=after,
        original_bytes=original,
        backup_bytes=b"not-the-original",
        requested_prompt="new prompt",
        receipt=receipt,
    )

    assert not result.ok
    assert "invariant changed: model" in result.errors
    assert "backup is not byte-exact" in result.errors


def test_contract_rejects_sensitive_diff_and_checks_rollback():
    before, after, original, receipt = valid_transaction()
    receipt["diff_summary"] = "token=super-secret-value"
    adapter = AntigravityPromptRepairContractAdapter()

    result = adapter.verify(
        before=before,
        after=after,
        original_bytes=original,
        backup_bytes=original,
        requested_prompt="new prompt",
        receipt=receipt,
    )
    assert "receipt diff_summary contains sensitive text" in result.errors

    with pytest.raises(PromptRepairContractError, match="rollback did not restore"):
        adapter.verify_rollback(
            original_bytes=original,
            restored_bytes=b"different",
            receipt={"rollback": True},
        )
    adapter.verify_rollback(
        original_bytes=original,
        restored_bytes=original,
        receipt={"rollback": True},
    )
