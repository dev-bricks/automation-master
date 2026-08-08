from __future__ import annotations

from datetime import datetime, timezone

import pytest

from automation_master.retention import (
    ReceiptRetentionClass,
    ReceiptRetentionPolicy,
    project_receipt,
    project_receipts,
)
from automation_master.store import EventStore


def append_receipt(store: EventStore, *, created_at: str, run_id: str = "run-1"):
    return store.append(
        node_id="node-a",
        budget_epoch="epoch-1",
        event_type="RECEIPT_RECORDED",
        entity_type="run",
        entity_id=run_id,
        dedupe_key=f"receipt:{run_id}",
        created_at=created_at,
        payload={
            "run_id": run_id,
            "outcome": "SUCCESS",
            "useful": True,
            "details": {"result": "kept", "nested": {"count": 1}},
        },
    )


def test_detailed_projection_keeps_details_without_mutating_event(tmp_path):
    store = EventStore(tmp_path / "ledger.db")
    event = append_receipt(store, created_at="2026-08-08T08:00:00+00:00")
    policy = ReceiptRetentionPolicy(detailed_days=30)
    now = datetime(2026, 8, 8, 12, tzinfo=timezone.utc)

    projected = project_receipt(event, policy=policy, now=now)

    assert projected["retention_class"] == ReceiptRetentionClass.DETAILED.value
    assert projected["details_retained"] is True
    assert projected["details"]["nested"]["count"] == 1
    assert projected["payload_hash"] == event.payload_hash
    projected["details"]["nested"]["count"] = 99
    assert event.payload["details"]["nested"]["count"] == 1
    assert store.count() == 1


def test_old_projection_drops_details_but_preserves_audit_metadata(tmp_path):
    store = EventStore(tmp_path / "ledger.db")
    event = append_receipt(store, created_at="2026-06-01T08:00:00Z")
    policy = ReceiptRetentionPolicy(detailed_days=30)
    now = datetime(2026, 8, 8, 12, tzinfo=timezone.utc)

    projected = project_receipt(event, policy=policy, now=now)

    assert projected["retention_class"] == ReceiptRetentionClass.AUDIT_SUMMARY.value
    assert projected["details_retained"] is False
    assert projected["details"] is None
    assert projected["payload_hash"] == event.payload_hash
    assert projected["event_id"] == event.event_id
    assert projected["outcome"] == "SUCCESS"
    assert projected["useful"] is True
    assert store.get(event_id=event.event_id) == event


def test_projection_is_bounded_to_receipt_events_and_valid_policy(tmp_path):
    store = EventStore(tmp_path / "ledger.db")
    other = store.append(
        node_id="node-a",
        budget_epoch="epoch-1",
        event_type="TEST",
        entity_type="fixture",
        entity_id="one",
        payload={"value": 1},
        created_at="2026-08-08T08:00:00+00:00",
    )
    with pytest.raises(ValueError, match="RECEIPT_RECORDED"):
        project_receipt(
            other,
            policy=ReceiptRetentionPolicy(),
            now=datetime(2026, 8, 8, tzinfo=timezone.utc),
        )
    with pytest.raises(ValueError, match="non-negative"):
        ReceiptRetentionPolicy(detailed_days=-1)
    with pytest.raises(ValueError, match="timezone-aware"):
        ReceiptRetentionPolicy().classify(
            "2026-08-08T08:00:00+00:00", now=datetime(2026, 8, 8)
        )


def test_project_receipts_preserves_order_and_hashes(tmp_path):
    store = EventStore(tmp_path / "ledger.db")
    first = append_receipt(store, created_at="2026-08-08T08:00:00+00:00", run_id="run-1")
    second = append_receipt(store, created_at="2026-06-01T08:00:00+00:00", run_id="run-2")

    projected = project_receipts(
        [first, second],
        policy=ReceiptRetentionPolicy(detailed_days=30),
        now=datetime(2026, 8, 8, tzinfo=timezone.utc),
    )

    assert [item["run_id"] for item in projected] == ["run-1", "run-2"]
    assert [item["payload_hash"] for item in projected] == [
        first.payload_hash,
        second.payload_hash,
    ]
