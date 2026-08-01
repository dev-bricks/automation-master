"""Versioned synthetic transit runner for the V4-14 two-host pilot.

Builds closed snapshots of automation-master-shaped databases, exchanges them
through a peer-inbox directory (the trusted-peer SFTP channel mounts there in
production; tests use a plain directory), and merges with the
AutomationEventMergePolicy. Never copies live WAL/SHM files; never writes into
OneDrive; every step emits hashes for receipts.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .adapters.sqlite_transit import AutomationEventMergePolicy
from .store import EventStore

SCHEMA_USER_VERSION = 1


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


@dataclass(frozen=True)
class SyntheticEvent:
    node_id: str
    entity_id: str
    payload: dict[str, Any]
    tombstone: bool = False
    dedupe_key: str | None = None
    event_id: str | None = None


def create_synthetic_db(path: Path, events: list[SyntheticEvent]) -> str:
    """Create a fresh automation-master-shaped DB; returns its sha256."""
    path = Path(path)
    if path.exists():
        raise FileExistsError(f"refusing to overwrite synthetic db: {path}")
    store = EventStore(path)
    for event in events:
        store.append(
            node_id=event.node_id,
            budget_epoch="synthetic-pilot",
            event_type="synthetic",
            entity_type="pilot",
            entity_id=event.entity_id,
            event_version=1,
            payload=event.payload,
            tombstone=event.tombstone,
            dedupe_key=event.dedupe_key,
            event_id=event.event_id,
        )
    return _sha256_file(path)


def _seal_db(db_path: Path) -> None:
    """Checkpoint and leave WAL mode so no sidecar files remain."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        conn.execute("PRAGMA journal_mode=DELETE")
    finally:
        conn.close()


def snapshot_db(
    source: Path,
    snapshot_dir: Path,
    *,
    seal_source: bool = True,
) -> tuple[Path, str]:
    """Closed snapshot via the sqlite backup API (never a raw file copy).

    With the default ``seal_source=True`` the source is sealed (checkpoint +
    journal_mode=DELETE) and any remaining WAL/SHM/journal sidecar afterwards
    fails closed. Pass ``seal_source=False`` for **live** databases: the source
    is never mutated (no journal mode change, no sidecar assertion on it) —
    the snapshot alone is sealed.
    """
    source = Path(source)
    if not source.is_file():
        raise FileNotFoundError(source)
    if seal_source:
        _seal_db(source)
        _assert_no_sidecars(source)
    snapshot_dir = Path(snapshot_dir)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    target = snapshot_dir / (source.stem + ".snapshot.db")
    if target.exists():
        target.unlink()
    src = sqlite3.connect(source)
    dst = sqlite3.connect(target)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    _seal_db(target)
    _assert_no_sidecars(target)
    return target, _sha256_file(target)


def _assert_no_sidecars(db_path: Path) -> None:
    for suffix in ("-wal", "-shm", "-journal"):
        if Path(str(db_path) + suffix).exists():
            raise RuntimeError(f"live sqlite sidecar present: {db_path}{suffix}")


def push_to_inbox(snapshot: Path, inbox: Path) -> tuple[Path, str]:
    """Atomic publish into the peer inbox (temp file + os.replace)."""
    inbox = Path(inbox)
    inbox.mkdir(parents=True, exist_ok=True)
    target = inbox / snapshot.name
    digest = _sha256_file(snapshot)
    with tempfile.NamedTemporaryFile(
        dir=inbox, prefix=".tmp-", delete=False
    ) as handle:
        tmp = Path(handle.name)
        handle.write(snapshot.read_bytes())
    os.replace(tmp, target)
    if _sha256_file(target) != digest:
        raise RuntimeError("inbox publish hash mismatch")
    return target, digest


def pull_peer_snapshots(inbox: Path, own_stem: str) -> list[Path]:
    """List peer snapshots in the inbox (own snapshots excluded by stem)."""
    inbox = Path(inbox)
    return sorted(
        p for p in inbox.glob("*.snapshot.db") if not p.name.startswith(own_stem)
    )


def merge_snapshot(
    local_db: Path,
    snapshot: Path,
    policy: AutomationEventMergePolicy | None = None,
) -> Any:
    """Merge one peer snapshot into the local DB; returns the merge report."""
    policy = policy or AutomationEventMergePolicy()
    local = sqlite3.connect(local_db)
    remote = sqlite3.connect(snapshot)
    try:
        report = policy.merge(local, remote, snapshot)
        local.commit()
    finally:
        remote.close()
        local.close()
    return report


def write_receipt(path: Path, receipt: dict[str, Any]) -> str:
    """Atomic receipt write; returns the receipt sha256."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    with tempfile.NamedTemporaryFile(
        dir=path.parent, prefix=".tmp-", delete=False, mode="w", encoding="utf-8"
    ) as handle:
        tmp = Path(handle.name)
        handle.write(encoded)
    os.replace(tmp, path)
    return _sha256_file(path)


def build_pilot_events(
    node_id: str,
    shared_prefix: str,
    unique_count: int = 3,
    include_tombstone: bool = True,
    include_credential_probe: bool = True,
) -> list[SyntheticEvent]:
    """Deterministic synthetic event set for one pilot node."""
    events: list[SyntheticEvent] = []
    events.append(
        SyntheticEvent(
            node_id="pilot-shared",
            entity_id=f"{shared_prefix}-shared",
            payload={"kind": "shared-baseline", "origin": "pilot"},
            dedupe_key=f"{shared_prefix}-shared-dedupe",
            event_id=f"{shared_prefix}-shared-event",
        )
    )
    for index in range(unique_count):
        events.append(
            SyntheticEvent(
                node_id=node_id,
                entity_id=f"{node_id}-unique-{index}",
                payload={"kind": "unique", "index": index, "node": node_id},
            )
        )
    if include_tombstone:
        events.append(
            SyntheticEvent(
                node_id=node_id,
                entity_id=f"{node_id}-retired",
                payload={"kind": "retired-marker"},
                tombstone=True,
                dedupe_key=f"{node_id}-retired-dedupe",
            )
        )
    if include_credential_probe:
        events.append(
            SyntheticEvent(
                node_id=node_id,
                entity_id=f"{node_id}-credential-probe",
                payload={"note": "api_key= pilot-probe (synthetic, no secret)"},
                dedupe_key=f"{node_id}-credential-probe-dedupe",
            )
        )
    return events


def pilot_receipt(
    *,
    node_id: str,
    db_path: Path,
    db_hash_before: str,
    db_hash_after: str,
    merges: list[dict[str, Any]],
    schema_user_version: int,
) -> dict[str, Any]:
    return {
        "schema": "ellmos.sqlite-transit-synthetic-pilot-receipt.v1",
        "observed_at": _utc_stamp(),
        "node_id": node_id,
        "db": {
            "path": str(db_path),
            "sha256_before": db_hash_before,
            "sha256_after": db_hash_after,
        },
        "schema_user_version": schema_user_version,
        "merges": merges,
        "non_claims": [
            "Synthetic databases only; no live automation-master.db touched.",
            "No WAL/SHM file was copied; snapshots via sqlite backup API.",
            "No ledger pruning performed.",
        ],
    }


__all__ = [
    "SyntheticEvent",
    "build_pilot_events",
    "create_synthetic_db",
    "merge_snapshot",
    "pilot_receipt",
    "pull_peer_snapshots",
    "push_to_inbox",
    "snapshot_db",
    "write_receipt",
]
