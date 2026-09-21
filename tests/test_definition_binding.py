from __future__ import annotations

from dataclasses import replace

import pytest

from automation_master import (
    AutomationDefinitionBinding,
    AutomationSpec,
    EventStore,
    ExecutionClass,
    MutationClass,
)
from automation_master.models import canonical_json, content_hash
from automation_master.service import AutomationMaster


def master_for(tmp_path, name="ledger.db"):
    return AutomationMaster(EventStore(tmp_path / name), node_id="test-node")


def registered_binding(
    master,
    *,
    version=1,
    execution_class=ExecutionClass.PINNED_RUNTIME_RELEASE,
    definition_commit="d948773c4a79b994add255803626e69f840d27c2",
    definition_content_hash=None,
    execution_pin="b" * 64,
):
    registration = master.register_automation(
        AutomationSpec(
            "automation-a",
            "family-a",
            "variant-a",
            MutationClass.READ_ONLY_REDUNDANT,
            version=version,
        )
    )
    return AutomationDefinitionBinding(
        automation_id="automation-a",
        definition_version=version,
        automation_payload_hash=registration.payload_hash,
        definition_source="repo://dev-bricks/automation-master",
        definition_branch="main",
        definition_commit=definition_commit,
        definition_content_hash=definition_content_hash,
        owner_ref="module:automation-registry",
        provider_ref="provider:registry-declared",
        execution_class=execution_class,
        execution_pin=(
            execution_pin if execution_class != ExecutionClass.APP_NATIVE else execution_pin
        ),
    )


def projection_item(master):
    return master.definition_binding_projection()["definitions"][0]


def test_binding_is_version_bound_idempotent_and_content_free(tmp_path):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    first = master.bind_automation_definition(binding)
    second = master.bind_automation_definition(binding)
    assert first.event_id == second.event_id
    assert master.get_automation_definition_binding("automation-a", 1) == binding
    item = projection_item(master)
    assert item["declaration_status"] == "declared"
    assert set(item["functions"].values()) == {"declared"}
    assert item["unavailable_reasons"] == {}
    assert "automation-a" not in str(item)
    assert "provider_ref" not in str(item)
    assert master.definition_binding_projection()["runtime_state"] == "not-observed"


def test_active_registration_declares_only_identity_until_bound(tmp_path):
    master = master_for(tmp_path)
    registered_binding(master)
    item = projection_item(master)
    assert item["declaration_status"] == "partial"
    assert item["functions"]["automation-definition-identity"] == "declared"
    assert {
        name: state
        for name, state in item["functions"].items()
        if name != "automation-definition-identity"
    } == {
        "definition-version-and-branch-reference": "unavailable",
        "provider-binding-reference": "unavailable",
        "declared-owner-and-execution-class": "unavailable",
    }
    assert set(item["unavailable_reasons"].values()) == {"missing_definition_binding"}


def test_binding_rejects_missing_hash_mismatch_and_tombstone_without_append(tmp_path):
    master = master_for(tmp_path)
    missing = AutomationDefinitionBinding(
        automation_id="missing",
        definition_version=1,
        automation_payload_hash="a" * 64,
        definition_source="repo://dev-bricks/automation-master",
        definition_branch="main",
        definition_commit="d948773c4a79b994add255803626e69f840d27c2",
        definition_content_hash=None,
        owner_ref="module:automation-registry",
        provider_ref="provider:registry-declared",
        execution_class=ExecutionClass.APP_NATIVE,
    )
    before = master.store.count()
    with pytest.raises(ValueError, match="missing_registered_definition"):
        master.bind_automation_definition(missing)
    assert master.store.count() == before

    binding = registered_binding(master)
    mismatch = replace(binding, automation_payload_hash="c" * 64)
    before = master.store.count()
    with pytest.raises(ValueError, match="payload hash"):
        master.bind_automation_definition(mismatch)
    assert master.store.count() == before

    tombstone_master = master_for(tmp_path, "tombstone.db")
    registration = tombstone_master.register_automation(
        AutomationSpec("automation-a", "family-a", "variant-a", MutationClass.READ_ONLY_REDUNDANT),
        tombstone=True,
    )
    tombstoned = replace(binding, automation_payload_hash=registration.payload_hash)
    before = tombstone_master.store.count()
    with pytest.raises(ValueError, match="tombstoned_registered_definition"):
        tombstone_master.bind_automation_definition(tombstoned)
    assert tombstone_master.store.count() == before


def test_ambiguous_registered_version_rejects_binding_without_append(tmp_path):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    registration = master.store.get(dedupe_key="automation:automation-a:v1")
    assert registration is not None
    master.store.append(
        node_id="other-node",
        budget_epoch="registry",
        event_type="AUTOMATION_REGISTERED",
        entity_type="automation",
        entity_id="automation-a",
        event_version=1,
        dedupe_key="imported-duplicate:automation-a:v1",
        payload=registration.payload,
    )
    before = master.store.count()
    with pytest.raises(ValueError, match="ambiguous_registered_definition"):
        master.bind_automation_definition(binding)
    assert master.store.count() == before
    item = projection_item(master)
    assert set(item["functions"].values()) == {"unavailable"}
    assert set(item["unavailable_reasons"].values()) == {"ambiguous_registered_definition"}


def test_imported_identical_binding_is_idempotent_but_conflicts_never_append(tmp_path):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    imported = master.store.append(
        node_id="imported-node",
        budget_epoch="registry",
        event_type="AUTOMATION_DEFINITION_BOUND",
        entity_type="automation-definition",
        entity_id=binding.automation_id,
        event_version=binding.definition_version,
        dedupe_key="imported-identical-binding",
        payload=binding.as_payload(),
    )
    before = master.store.count()
    assert master.bind_automation_definition(binding) == imported
    assert master.store.count() == before

    conflict_master = master_for(tmp_path, "import-conflict.db")
    conflict_binding = registered_binding(conflict_master)
    conflict_master.store.append(
        node_id="other-imported-node",
        budget_epoch="registry",
        event_type="AUTOMATION_DEFINITION_BOUND",
        entity_type="automation-definition",
        entity_id=conflict_binding.automation_id,
        event_version=conflict_binding.definition_version,
        dedupe_key="imported-conflicting-binding",
        payload=replace(
            conflict_binding,
            owner_ref="module:other-owner",
        ).as_payload(),
    )
    before = conflict_master.store.count()
    with pytest.raises(ValueError, match="conflicts"):
        conflict_master.bind_automation_definition(conflict_binding)
    assert conflict_master.store.count() == before

    ambiguous_master = master_for(tmp_path, "import-ambiguous.db")
    ambiguous_binding = registered_binding(ambiguous_master)
    for dedupe_key in ("imported-one", "imported-two"):
        ambiguous_master.store.append(
            node_id="imported-node",
            budget_epoch="registry",
            event_type="AUTOMATION_DEFINITION_BOUND",
            entity_type="automation-definition",
            entity_id=ambiguous_binding.automation_id,
            event_version=ambiguous_binding.definition_version,
            dedupe_key=dedupe_key,
            payload=ambiguous_binding.as_payload(),
        )
    before = ambiguous_master.store.count()
    with pytest.raises(ValueError, match="ambiguous"):
        ambiguous_master.bind_automation_definition(ambiguous_binding)
    assert ambiguous_master.store.count() == before

    tombstone_master = master_for(tmp_path, "import-tombstone.db")
    tombstone_binding = registered_binding(tombstone_master)
    tombstone_master.store.append(
        node_id="imported-node",
        budget_epoch="registry",
        event_type="AUTOMATION_DEFINITION_BOUND",
        entity_type="automation-definition",
        entity_id=tombstone_binding.automation_id,
        event_version=tombstone_binding.definition_version,
        tombstone=True,
        dedupe_key="imported-tombstone",
        payload=tombstone_binding.as_payload(),
    )
    before = tombstone_master.store.count()
    with pytest.raises(ValueError, match="invalid_definition_binding"):
        tombstone_master.bind_automation_definition(tombstone_binding)
    assert tombstone_master.store.count() == before


def test_conflicting_same_version_binding_rolls_back_and_version_change_is_explicit(tmp_path):
    master = master_for(tmp_path)
    first = registered_binding(master, version=1)
    master.bind_automation_definition(first)
    before = master.store.count()
    with pytest.raises(ValueError, match="conflicts"):
        master.bind_automation_definition(replace(first, owner_ref="module:other-owner"))
    assert master.store.count() == before

    version_two = registered_binding(
        master,
        version=2,
        definition_commit=None,
        definition_content_hash="a" * 64,
        execution_pin="c" * 40,
    )
    master.bind_automation_definition(version_two)
    assert master.get_automation_definition_binding("automation-a", 1) == first
    assert master.get_automation_definition_binding("automation-a", 2) == version_two


def test_registration_payload_identity_must_match_event_envelope(tmp_path):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    registration = master.store.get(dedupe_key="automation:automation-a:v1")
    assert registration is not None
    payload = dict(registration.payload)
    payload["version"] = 2
    with master.store.immediate() as conn:
        conn.execute(
            "UPDATE events SET payload_json=?, payload_hash=? WHERE dedupe_key=?",
            (
                canonical_json(payload),
                content_hash(payload),
                "automation:automation-a:v1",
            ),
        )
    with pytest.raises(ValueError, match="invalid_registered_definition"):
        master.bind_automation_definition(binding)
    item = projection_item(master)
    assert set(item["functions"].values()) == {"unavailable"}


def test_corrupt_registration_event_is_never_declared_or_bindable(tmp_path):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    with master.store.immediate() as conn:
        conn.execute(
            "UPDATE events SET payload_hash=? WHERE dedupe_key=?",
            ("0" * 64, "automation:automation-a:v1"),
        )
    with pytest.raises(ValueError, match="invalid_registered_definition"):
        master.bind_automation_definition(binding)
    with pytest.raises(ValueError, match="invalid_registered_definition"):
        master.get_automation_definition_binding("automation-a", 1)
    item = projection_item(master)
    assert set(item["functions"].values()) == {"unavailable"}
    assert set(item["unavailable_reasons"].values()) == {"invalid_registered_definition"}


def test_binding_payload_identity_must_match_event_envelope(tmp_path):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    master.bind_automation_definition(binding)
    payload = binding.as_payload()
    payload["definition_version"] = 2
    with master.store.immediate() as conn:
        conn.execute(
            "UPDATE events SET payload_json=?, payload_hash=? WHERE dedupe_key=?",
            (
                canonical_json(payload),
                content_hash(payload),
                "automation-definition-binding:automation-a:v1",
            ),
        )
    with pytest.raises(ValueError, match="invalid_definition_binding"):
        master.get_automation_definition_binding("automation-a", 1)
    item = projection_item(master)
    assert item["functions"]["automation-definition-identity"] == "declared"
    assert set(item["unavailable_reasons"].values()) == {"invalid_definition_binding"}


@pytest.mark.parametrize(
    "column, value",
    [
        ("payload_hash", "0" * 64),
        ("entity_type", "wrong-definition"),
        ("tombstone", 1),
    ],
)
def test_corrupt_or_tombstoned_binding_event_keeps_only_identity_declared(tmp_path, column, value):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    master.bind_automation_definition(binding)
    with master.store.immediate() as conn:
        conn.execute(
            f"UPDATE events SET {column}=? WHERE dedupe_key=?",
            (value, "automation-definition-binding:automation-a:v1"),
        )
    with pytest.raises(ValueError, match="invalid_definition_binding"):
        master.get_automation_definition_binding("automation-a", 1)
    item = projection_item(master)
    assert item["functions"]["automation-definition-identity"] == "declared"
    assert set(item["unavailable_reasons"].values()) == {"invalid_definition_binding"}


def test_binding_rejects_unsafe_refs_and_preserves_native_execution_contract(tmp_path):
    master = master_for(tmp_path)
    binding = registered_binding(master)
    with pytest.raises(ValueError, match="credential-free"):
        master.bind_automation_definition(
            replace(binding, definition_source="repo://token@host/repo")
        )
    with pytest.raises(ValueError, match="definition_branch"):
        master.bind_automation_definition(replace(binding, definition_branch="main\nother"))
    with pytest.raises(ValueError, match="owner_ref"):
        master.bind_automation_definition(replace(binding, owner_ref="module:owner name"))
    with pytest.raises(ValueError, match="execution_pin"):
        master.bind_automation_definition(replace(binding, execution_pin=None))
    with pytest.raises(ValueError, match="definition source"):
        master.bind_automation_definition(
            replace(
                binding,
                definition_commit=None,
                definition_content_hash=None,
            )
        )

    token_watcher = replace(binding, definition_source="repo://ellmos-ai/token-watcher")
    master.bind_automation_definition(token_watcher)
    assert (
        master.get_automation_definition_binding("automation-a", 1).definition_source
        == "repo://ellmos-ai/token-watcher"
    )

    app_master = master_for(tmp_path, "app-native.db")
    app_native = registered_binding(
        app_master,
        execution_class=ExecutionClass.APP_NATIVE,
        execution_pin=None,
        definition_content_hash="d" * 64,
    )
    app_master.bind_automation_definition(app_native)
    assert app_master.get_automation_definition_binding("automation-a", 1).execution_pin is None

    pinned_master = master_for(tmp_path, "sha256-pin.db")
    sha256_pin = registered_binding(
        pinned_master,
        execution_pin="sha256:" + "e" * 64,
    )
    pinned_master.bind_automation_definition(sha256_pin)
    assert (
        pinned_master.get_automation_definition_binding("automation-a", 1).execution_pin
        == "sha256:" + "e" * 64
    )
