from __future__ import annotations

from dataclasses import dataclass

from automation_master.adapters.sqlite_transit import AutomationEventMergePolicy
from automation_master.service import AutomationMaster
from automation_master.store import EventStore


@dataclass(frozen=True)
class Snapshot:
    source_node: str


def merge(source: EventStore, target: EventStore, source_node: str):
    policy = AutomationEventMergePolicy()
    with target.connect() as local, source.connect() as remote:
        return policy.merge(local, remote, Snapshot(source_node))


def test_offline_hosts_and_stale_snapshots_converge(tmp_path):
    workstation_store = EventStore(tmp_path / "workstation.db")
    laptop_store = EventStore(tmp_path / "laptop.db")
    workstation = AutomationMaster(workstation_store, node_id="workstation")
    laptop = AutomationMaster(laptop_store, node_id="laptop")

    workstation.allocate_budget(
        budget_epoch="e1",
        scope_id="workstation",
        credits=4,
        allocation_id="workstation-envelope",
    )
    laptop.allocate_budget(
        budget_epoch="e1",
        scope_id="laptop",
        credits=2,
        allocation_id="laptop-envelope",
    )
    first = merge(workstation_store, laptop_store, "workstation")
    assert first.inserted == 1

    workstation.register_family("research", name="Research", version=1)
    second = merge(workstation_store, laptop_store, "workstation")
    assert second.inserted == 1
    merge(laptop_store, workstation_store, "laptop")

    assert workstation_store.count() == laptop_store.count() == 3
    assert workstation.budget_state("e1", "workstation").available == 4
    assert laptop.budget_state("e1", "laptop").available == 2
    assert workstation.registry() == laptop.registry()


def test_merge_is_idempotent(tmp_path):
    source = EventStore(tmp_path / "source.db")
    target = EventStore(tmp_path / "target.db")
    AutomationMaster(source, node_id="source").register_family("one", name="One")
    first = merge(source, target, "source")
    second = merge(source, target, "source")
    assert first.inserted == 1
    assert second.inserted == 0
    assert second.unchanged == 1
