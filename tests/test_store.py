from __future__ import annotations

import sqlite3

import pytest

from automation_master.store import EventConflictError, EventStore


def test_schema_migration_and_idempotent_event(tmp_path):
    db = tmp_path / "ledger.db"
    with sqlite3.connect(db) as connection:
        connection.execute("PRAGMA user_version=0")

    store = EventStore(db)
    assert store.schema_version() == 1
    first = store.append(
        node_id="node-a",
        budget_epoch="e1",
        event_type="TEST",
        entity_type="fixture",
        entity_id="one",
        dedupe_key="fixture:one",
        payload={"value": 1},
    )
    repeated = store.append(
        node_id="node-a",
        budget_epoch="e1",
        event_type="TEST",
        entity_type="fixture",
        entity_id="one",
        dedupe_key="fixture:one",
        payload={"value": 1},
    )
    assert repeated.event_id == first.event_id
    assert store.count() == 1


def test_duplicate_identity_with_different_content_fails_closed(tmp_path):
    store = EventStore(tmp_path / "ledger.db")
    store.append(
        node_id="node-a",
        budget_epoch="e1",
        event_type="TEST",
        entity_type="fixture",
        entity_id="one",
        dedupe_key="same",
        payload={"value": 1},
    )
    with pytest.raises(EventConflictError):
        store.append(
            node_id="node-a",
            budget_epoch="e1",
            event_type="TEST",
            entity_type="fixture",
            entity_id="one",
            dedupe_key="same",
            payload={"value": 2},
        )


def test_import_rejects_payload_hash_mismatch(tmp_path):
    store = EventStore(tmp_path / "ledger.db")
    with pytest.raises(EventConflictError):
        store.import_events(
            [
                {
                    "event_id": "evt-1",
                    "node_id": "node-a",
                    "budget_epoch": "e1",
                    "event_type": "TEST",
                    "entity_type": "fixture",
                    "entity_id": "one",
                    "event_version": 1,
                    "created_at": "2026-07-28T00:00:00+00:00",
                    "payload": {"value": 1},
                    "payload_hash": "0" * 64,
                }
            ]
        )
