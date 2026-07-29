"""Immutable-event merge policy compatible with sqlite-transit-sync."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..models import canonical_json, content_hash
from ..store import EventConflictError


@dataclass(frozen=True)
class LocalMergeReport:
    snapshot: str
    source_node: str
    inserted: int
    updated: int
    unchanged: int
    skipped_tables: list[str]
    tables: dict[str, dict[str, int]]


class AutomationEventMergePolicy:
    """Union immutable events; never update or apply last-write-wins."""

    def merge(
        self,
        local: sqlite3.Connection,
        remote: sqlite3.Connection,
        snapshot: Any,
    ) -> Any:
        local.row_factory = sqlite3.Row
        remote.row_factory = sqlite3.Row
        source_node = str(
            getattr(snapshot, "node_id", getattr(snapshot, "source_node", "unknown"))
        )
        snapshot_value = getattr(snapshot, "path", snapshot)
        snapshot_name = (
            Path(snapshot_value).name
            if isinstance(snapshot_value, (str, Path))
            else str(snapshot_value)
        )
        rows = remote.execute("SELECT * FROM events ORDER BY event_id").fetchall()
        inserted = unchanged = 0
        for row in rows:
            existing = local.execute(
                "SELECT * FROM events WHERE event_id=? OR "
                "(? IS NOT NULL AND dedupe_key=?)",
                (row["event_id"], row["dedupe_key"], row["dedupe_key"]),
            ).fetchone()
            if existing:
                if not self._equivalent(existing, row):
                    raise EventConflictError(f"merge identity conflict for {row['event_id']}")
                unchanged += 1
                continue
            payload = json.loads(row["payload_json"])
            if content_hash(payload) != row["payload_hash"]:
                raise EventConflictError(f"merge payload hash mismatch for {row['event_id']}")
            local.execute(
                """
                INSERT INTO events(
                    event_id, node_id, budget_epoch, event_type, entity_type, entity_id,
                    event_version, created_at, tombstone, dedupe_key, payload_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                tuple(row),
            )
            inserted += 1
        report_type = self._report_type()
        return report_type(
            snapshot=snapshot_name,
            source_node=source_node,
            inserted=inserted,
            updated=0,
            unchanged=unchanged,
            skipped_tables=[],
            tables={"events": {"inserted": inserted, "updated": 0, "unchanged": unchanged}},
        )

    @staticmethod
    def _equivalent(left: sqlite3.Row, right: sqlite3.Row) -> bool:
        keys = (
            "node_id",
            "budget_epoch",
            "event_type",
            "entity_type",
            "entity_id",
            "event_version",
            "tombstone",
            "dedupe_key",
            "payload_hash",
        )
        if any(left[key] != right[key] for key in keys):
            return False
        return canonical_json(json.loads(left["payload_json"])) == canonical_json(
            json.loads(right["payload_json"])
        )

    @staticmethod
    def _report_type() -> Any:
        try:
            from sqlite_transit_sync import MergeReport

            return MergeReport
        except ImportError:
            return LocalMergeReport
