from pathlib import Path

import pytest

from automation_master import EnforcementMode
from automation_master.adapters.system_gap import (
    DeploymentPlan,
    SystemGapAdapter,
    TrustPolicy,
)


def make_plan(adapter, manifest, target, **overrides):
    values = {
        "module_id": "automation-master",
        "module_version": "0.1.0",
        "source_id": "gap-master",
        "target_node": "workstation",
        "target_path": str(target),
        "manifest_hash": adapter.manifest_hash(manifest),
        "mode": EnforcementMode.SHADOW,
        "activate": False,
    }
    values.update(overrides)
    return DeploymentPlan(**values)


def test_default_trust_policy_fails_closed(tmp_path):
    manifest = {"id": "automation-master", "version": "0.1.0"}
    adapter = SystemGapAdapter(local_node="workstation")
    errors = adapter.validate(make_plan(adapter, manifest, tmp_path), manifest=manifest)
    assert "untrusted source_id" in errors
    assert "target path outside trusted roots" in errors


def test_trusted_disabled_or_shadow_plan_and_healthcheck(tmp_path):
    root = Path(tmp_path)
    manifest = {"id": "automation-master", "version": "0.1.0"}
    adapter = SystemGapAdapter(
        local_node="workstation",
        trust_policy=TrustPolicy(
            allowed_sources=("gap-master",),
            allowed_target_roots=(str(root),),
        ),
    )
    plan = make_plan(adapter, manifest, root / "automation-master")
    assert adapter.validate(plan, manifest=manifest) == []
    assert adapter.healthcheck(plan, observed_hash=plan.manifest_hash)
    assert adapter.rollback_plan(plan, previous_version="0.0.9")["activation"] == "disabled"


def test_foreign_slot_hash_version_and_enforcement_are_rejected(tmp_path):
    manifest = {"id": "automation-master", "version": "0.1.0"}
    adapter = SystemGapAdapter(
        local_node="workstation",
        trust_policy=TrustPolicy(
            allowed_sources=("gap-master",),
            allowed_target_roots=(str(tmp_path),),
        ),
    )
    plan = make_plan(
        adapter,
        manifest,
        tmp_path,
        target_node="laptop",
        manifest_hash="0" * 64,
        module_version="1.0.0",
        mode=EnforcementMode.ENFORCED,
        activate=True,
    )
    errors = adapter.validate(plan, manifest=manifest)
    assert "foreign target_node" in errors
    assert "manifest hash mismatch" in errors
    assert "manifest version mismatch" in errors
    assert "enforcement mode not allowed" in errors
    assert "activation not allowed" in errors
    with pytest.raises(ValueError):
        adapter.require_valid(plan, manifest=manifest)


def test_foreign_manifest_identity_and_same_major_downgrade_are_rejected(tmp_path):
    manifest = {"id": "foreign-module", "version": "0.1.0"}
    adapter = SystemGapAdapter(
        local_node="workstation",
        trust_policy=TrustPolicy(
            allowed_sources=("gap-master",),
            allowed_target_roots=(str(tmp_path),),
        ),
    )
    plan = make_plan(adapter, manifest, tmp_path)
    errors = adapter.validate(plan, manifest=manifest, installed_version="0.2.0")
    assert "manifest module_id mismatch" in errors
    assert "downgrade blocked" in errors


def test_invalid_semantic_versions_fail_closed(tmp_path):
    manifest = {"id": "automation-master", "version": "0.1"}
    adapter = SystemGapAdapter(
        local_node="workstation",
        trust_policy=TrustPolicy(
            allowed_sources=("gap-master",),
            allowed_target_roots=(str(tmp_path),),
        ),
    )
    plan = make_plan(adapter, manifest, tmp_path, module_version="0.1")
    errors = adapter.validate(plan, manifest=manifest)
    assert "invalid semantic version: 0.1" in errors
