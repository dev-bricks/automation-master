"""Local two-node simulation tests for the V4-14 synthetic transit pilot."""

from __future__ import annotations

import sqlite3

import pytest

from automation_master.store import EventConflictError, EventStore
from automation_master.transit_runner import (
    SyntheticEvent,
    build_pilot_events,
    create_synthetic_db,
    merge_snapshot,
    pilot_receipt,
    pull_peer_snapshots,
    push_to_inbox,
    snapshot_db,
    write_receipt,
)


def _event_set(db_path):
    store = EventStore(db_path)
    return {
        (e.event_id, bool(e.tombstone), e.payload_hash)
        for e in store.events()
    }


def test_two_node_pilot_converges_with_tombstones(tmp_path):
    db_a = tmp_path / "node-a.db"
    db_b = tmp_path / "node-b.db"
    events_a = build_pilot_events("node-a", "pilot-20260731")
    events_b = build_pilot_events("node-b", "pilot-20260731")
    create_synthetic_db(db_a, events_a)
    create_synthetic_db(db_b, events_b)

    snap_a, hash_a = snapshot_db(db_a, tmp_path / "snapshots")
    snap_b, hash_b = snapshot_db(db_b, tmp_path / "snapshots")
    inbox_a, _ = push_to_inbox(snap_a, tmp_path / "inbox")
    inbox_b, _ = push_to_inbox(snap_b, tmp_path / "inbox")

    peer_of_a = pull_peer_snapshots(tmp_path / "inbox", "node-a")
    peer_of_b = pull_peer_snapshots(tmp_path / "inbox", "node-b")
    assert peer_of_a == [inbox_b]
    assert peer_of_b == [inbox_a]

    report_a = merge_snapshot(db_a, peer_of_a[0])
    report_b = merge_snapshot(db_b, peer_of_b[0])

    assert report_a.inserted == len(events_b) - 1  # shared event deduplicated
    assert report_a.unchanged == 1
    assert report_b.inserted == len(events_a) - 1
    assert report_b.unchanged == 1
    assert report_a.updated == 0 and report_b.updated == 0

    set_a = _event_set(db_a)
    set_b = _event_set(db_b)
    assert set_a == set_b
    assert any(tombstone == 1 for _, tombstone, _ in set_a)
    assert any(tombstone == 1 for _, tombstone, _ in set_b)


def test_merge_is_idempotent(tmp_path):
    db_source = tmp_path / "source.db"
    db_target = tmp_path / "target.db"
    create_synthetic_db(db_source, build_pilot_events("source", "idem"))
    create_synthetic_db(db_target, [])
    snapshot, _ = snapshot_db(db_source, tmp_path / "snap")

    first = merge_snapshot(db_target, snapshot)
    second = merge_snapshot(db_target, snapshot)

    assert first.inserted > 0
    assert second.inserted == 0
    assert second.unchanged == first.inserted


def test_conflicting_event_fails_closed(tmp_path):
    db_a = tmp_path / "a.db"
    db_b = tmp_path / "b.db"
    create_synthetic_db(
        db_a,
        [SyntheticEvent(node_id="a", entity_id="x", payload={"v": 1}, event_id="conflict-1")],
    )
    create_synthetic_db(
        db_b,
        [SyntheticEvent(node_id="b", entity_id="x", payload={"v": 2}, event_id="conflict-1")],
    )
    snapshot_b, _ = snapshot_db(db_b, tmp_path / "snap")
    with pytest.raises(EventConflictError):
        merge_snapshot(db_a, snapshot_b)


def test_snapshot_has_no_sidecars(tmp_path):
    db_path = tmp_path / "clean.db"
    create_synthetic_db(db_path, build_pilot_events("clean", "side"))
    snapshot, digest = snapshot_db(db_path, tmp_path / "snap")
    assert snapshot.exists()
    assert len(digest) == 64
    for suffix in ("-wal", "-shm", "-journal"):
        assert not (tmp_path / "snap" / (snapshot.name + suffix)).exists()


def test_receipt_write_is_atomic_and_hashed(tmp_path):
    receipt_path = tmp_path / "receipts" / "pilot.json"
    receipt = pilot_receipt(
        node_id="node-a",
        db_path=tmp_path / "node-a.db",
        db_hash_before="0" * 64,
        db_hash_after="1" * 64,
        merges=[{"snapshot": "node-b.snapshot.db", "inserted": 4, "unchanged": 1}],
        schema_user_version=1,
    )
    digest = write_receipt(receipt_path, receipt)
    assert receipt_path.exists()
    assert len(digest) == 64
    leftover = list((tmp_path / "receipts").glob(".tmp-*"))
    assert leftover == []


def test_push_to_inbox_is_hash_verified(tmp_path):
    db_path = tmp_path / "push.db"
    create_synthetic_db(db_path, build_pilot_events("push", "push"))
    snapshot, digest = snapshot_db(db_path, tmp_path / "snap")
    published, published_digest = push_to_inbox(snapshot, tmp_path / "inbox")
    assert published_digest == digest
    assert published.read_bytes() == snapshot.read_bytes()


def test_snapshot_of_live_db_never_mutates_the_source(tmp_path):
    db_path = tmp_path / "live.db"
    create_synthetic_db(db_path, build_pilot_events("live", "live"))
    # Offene Verbindung simuliert die laufende Live-DB (WAL bleibt bestehen)
    holder = sqlite3.connect(db_path)
    holder.execute("PRAGMA journal_mode=WAL")
    holder.execute("BEGIN IMMEDIATE")
    holder.execute(
        "INSERT INTO events(event_id,node_id,budget_epoch,event_type,"
        "entity_type,entity_id,event_version,created_at,tombstone,"
        "payload_json,payload_hash) VALUES('hold','live','e','t','t','t',"
        "1,'t',0,'{}','x')"
    )

    snapshot, digest = snapshot_db(db_path, tmp_path / "snap", seal_source=False)

    # Source unverändert: WAL-Zustand und Journal-Mode bleiben
    assert (tmp_path / "live.db-wal").exists()
    assert holder.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    holder.rollback()
    holder.close()
    # Snapshot ist dennoch versiegelt und vollständig
    assert len(digest) == 64
    check = sqlite3.connect(snapshot)
    assert check.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 6
    check.close()


def test_snapshot_seal_source_default_still_seals(tmp_path):
    db_path = tmp_path / "sealed.db"
    create_synthetic_db(db_path, build_pilot_events("sealed", "sealed"))
    snapshot, _ = snapshot_db(db_path, tmp_path / "snap")
    assert not (tmp_path / "sealed.db-wal").exists()
    conn = sqlite3.connect(db_path)
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "delete"
    conn.close()
