from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import pytest

from automation_master import (
    AutomationSpec,
    EnforcementMode,
    EventStore,
    MutationClass,
    RunClass,
)
from automation_master.adapters import CreditGateAdapter
from automation_master.service import AutomationMaster, CreditPolicy


def master_for(tmp_path, name: str = "ledger.db", node: str = "node-a"):
    return AutomationMaster(EventStore(tmp_path / name), node_id=node)


def test_registry_uses_versions_not_clock_time(tmp_path):
    master = master_for(tmp_path)
    old = AutomationSpec("auto", "family", "v1", MutationClass.READ_ONLY_REDUNDANT)
    new = AutomationSpec(
        "auto",
        "family",
        "v2",
        MutationClass.INDEPENDENT_REVIEW,
        version=2,
    )
    master.store.append(
        node_id="node-a",
        budget_epoch="registry",
        event_type="AUTOMATION_REGISTERED",
        entity_type="automation",
        entity_id="auto",
        event_version=1,
        dedupe_key="automation:auto:v1",
        created_at="2099-01-01T00:00:00+00:00",
        payload=old.as_payload(),
    )
    master.store.append(
        node_id="node-b",
        budget_epoch="registry",
        event_type="AUTOMATION_REGISTERED",
        entity_type="automation",
        entity_id="auto",
        event_version=2,
        dedupe_key="automation:auto:v2",
        created_at="2000-01-01T00:00:00+00:00",
        payload=new.as_payload(),
    )
    assert master.registry()["automations"]["auto"]["variant_id"] == "v2"


def test_no_work_preflight_consumes_no_credit(tmp_path):
    master = master_for(tmp_path)
    master.allocate_budget(
        budget_epoch="e1",
        scope_id="family",
        credits=3,
        allocation_id="seed",
    )
    gate = CreditGateAdapter(
        master,
        CreditPolicy(mode=EnforcementMode.ENFORCED),
    )
    decision = gate.authorize(
        run_id="run-no-work",
        budget_epoch="e1",
        scope_id="family",
        work_item_id="item-1",
        work_available=False,
        credits=1,
    )
    assert decision.status == "NO_WORK"
    state = master.budget_state("e1", "family")
    assert state.available == 3
    assert state.spent == 0
    assert state.held == 0


def test_late_no_work_releases_reservation_and_duplicate_receipt_is_idempotent(tmp_path):
    master = master_for(tmp_path)
    master.allocate_budget(
        budget_epoch="e1",
        scope_id="family",
        credits=2,
        allocation_id="seed",
    )
    gate = CreditGateAdapter(
        master,
        CreditPolicy(mode=EnforcementMode.SHADOW),
    )
    decision = gate.authorize(
        run_id="run-1",
        budget_epoch="e1",
        scope_id="family",
        work_item_id="item-1",
        work_available=True,
        credits=1,
    )
    assert decision.status == "RESERVED"
    assert master.budget_state("e1", "family").held == 1
    first = master.complete_run(run_id="run-1", outcome="NO_WORK", useful=False)
    second = master.complete_run(run_id="run-1", outcome="NO_WORK", useful=False)
    assert first.event_id == second.event_id
    state = master.budget_state("e1", "family")
    assert state.available == 2
    assert state.spent == 0


def test_concurrent_local_reservation_prevents_double_allocation(tmp_path):
    db = tmp_path / "ledger.db"
    setup = AutomationMaster(EventStore(db), node_id="setup")
    setup.allocate_budget(
        budget_epoch="e1",
        scope_id="family",
        credits=1,
        allocation_id="seed",
    )
    for run_id in ("run-a", "run-b"):
        setup.preflight(
            run_id=run_id,
            budget_epoch="e1",
            scope_id="family",
            work_item_id=run_id,
            work_available=True,
        )

    def reserve(run_id: str):
        worker = AutomationMaster(EventStore(db), node_id=run_id)
        return worker.reserve_credit(
            run_id=run_id,
            budget_epoch="e1",
            scope_id="family",
            credits=1,
            run_class=RunClass.COMPARABLE,
            policy=CreditPolicy(mode=EnforcementMode.ENFORCED),
        )

    with ThreadPoolExecutor(max_workers=2) as pool:
        decisions = list(pool.map(reserve, ("run-a", "run-b")))
    assert sorted(decision.status for decision in decisions) == [
        "BUDGET_DENIED",
        "RESERVED",
    ]
    assert setup.budget_state("e1", "family").held == 1


def test_enforced_denial_bounded_overdraft_and_critical_exemption(tmp_path):
    master = master_for(tmp_path)
    master.preflight(
        run_id="ordinary",
        budget_epoch="e1",
        scope_id="family",
        work_item_id="one",
        work_available=True,
    )
    denied = master.reserve_credit(
        run_id="ordinary",
        budget_epoch="e1",
        scope_id="family",
        credits=1,
        run_class=RunClass.COMPARABLE,
        policy=CreditPolicy(mode=EnforcementMode.ENFORCED),
    )
    assert denied.status == "BUDGET_DENIED"

    master.preflight(
        run_id="overdraft",
        budget_epoch="e1",
        scope_id="family",
        work_item_id="two",
        work_available=True,
    )
    overdraft = master.reserve_credit(
        run_id="overdraft",
        budget_epoch="e1",
        scope_id="family",
        credits=1,
        run_class=RunClass.COMPARABLE,
        policy=CreditPolicy(
            mode=EnforcementMode.ENFORCED,
            overdraft_limit=1,
            allow_critical_overdraft=True,
        ),
        critical_minimum_coverage=True,
    )
    assert overdraft.status == "BUDGET_OVERDRAFT"
    assert master.budget_state("e1", "family").available == -1

    master.preflight(
        run_id="safety",
        budget_epoch="e1",
        scope_id="family",
        work_item_id="three",
        work_available=True,
    )
    exempt = master.reserve_credit(
        run_id="safety",
        budget_epoch="e1",
        scope_id="family",
        credits=1,
        run_class=RunClass.SAFETY,
        policy=CreditPolicy(mode=EnforcementMode.ENFORCED),
    )
    assert exempt.status == "EXEMPT_CRITICAL_CLASS"


def test_disabled_and_shadow_modes_do_not_hard_stop(tmp_path):
    master = master_for(tmp_path)
    for run_id in ("disabled", "shadow"):
        master.preflight(
            run_id=run_id,
            budget_epoch="e1",
            scope_id="family",
            work_item_id=run_id,
            work_available=True,
        )
    disabled = master.reserve_credit(
        run_id="disabled",
        budget_epoch="e1",
        scope_id="family",
        credits=1,
        run_class=RunClass.COMPARABLE,
        policy=CreditPolicy(),
    )
    shadow = master.reserve_credit(
        run_id="shadow",
        budget_epoch="e1",
        scope_id="family",
        credits=1,
        run_class=RunClass.COMPARABLE,
        policy=CreditPolicy(mode=EnforcementMode.SHADOW),
    )
    assert disabled.status == "ALLOWED_DISABLED"
    assert shadow.status == "SHADOW_NEGATIVE"


def test_handover_return_and_epoch_isolation(tmp_path):
    master = master_for(tmp_path)
    master.allocate_budget(
        budget_epoch="e1",
        scope_id="host-a",
        credits=5,
        allocation_id="seed-a",
    )
    master.handover_budget(
        budget_epoch="e1",
        source_scope_id="host-a",
        target_scope_id="host-b",
        credits=2,
        transfer_id="a-to-b",
    )
    assert master.budget_state("e1", "host-a").available == 3
    assert master.budget_state("e1", "host-b").available == 2
    master.return_budget(
        budget_epoch="e1",
        source_scope_id="host-b",
        target_scope_id="host-a",
        credits=1,
        transfer_id="unused",
    )
    assert master.budget_state("e1", "host-a").available == 4
    assert master.budget_state("e1", "host-b").available == 1
    assert master.budget_state("e2", "host-a").available == 0


def test_receipt_with_different_retry_content_fails(tmp_path):
    master = master_for(tmp_path)
    decision = master.preflight(
        run_id="run",
        budget_epoch="e1",
        scope_id="family",
        work_item_id="item",
        work_available=False,
    )
    assert decision is not None
    master.complete_run(run_id="run", outcome="NO_WORK", useful=False)
    with pytest.raises(ValueError):
        master.complete_run(run_id="run", outcome="SUCCESS", useful=True)
