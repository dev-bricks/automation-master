"""Append-only SQLite event store.

Mutable balances are intentionally absent. Every projection is rebuilt from events.
"""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import canonical_json, content_hash, new_event_id, utc_now

SCHEMA_VERSION = 1


class EventConflictError(RuntimeError):
    """The same event ID or dedupe key was observed with different content."""


@dataclass(frozen=True)
class Event:
    event_id: str
    node_id: str
    budget_epoch: str
    event_type: str
    entity_type: str
    entity_id: str
    event_version: int
    created_at: str
    tombstone: bool
    dedupe_key: str | None
    payload: dict[str, Any]
    payload_hash: str

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> Event:
        return cls(
            event_id=row["event_id"],
            node_id=row["node_id"],
            budget_epoch=row["budget_epoch"],
            event_type=row["event_type"],
            entity_type=row["entity_type"],
            entity_id=row["entity_id"],
            event_version=row["event_version"],
            created_at=row["created_at"],
            tombstone=bool(row["tombstone"]),
            dedupe_key=row["dedupe_key"],
            payload=json.loads(row["payload_json"]),
            payload_hash=row["payload_hash"],
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "node_id": self.node_id,
            "budget_epoch": self.budget_epoch,
            "event_type": self.event_type,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "event_version": self.event_version,
            "created_at": self.created_at,
            "tombstone": self.tombstone,
            "dedupe_key": self.dedupe_key,
            "payload": self.payload,
            "payload_hash": self.payload_hash,
        }


class EventStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path).expanduser().resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._migrate()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA busy_timeout=30000")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _migrate(self) -> None:
        with self.connect() as conn:
            current = int(conn.execute("PRAGMA user_version").fetchone()[0])
            if current > SCHEMA_VERSION:
                raise RuntimeError(
                    f"database schema {current} is newer than supported {SCHEMA_VERSION}"
                )
            if current < 1:
                conn.executescript(
                    """
                    BEGIN IMMEDIATE;
                    CREATE TABLE IF NOT EXISTS schema_migrations (
                        version INTEGER PRIMARY KEY,
                        applied_at TEXT NOT NULL
                    );
                    CREATE TABLE IF NOT EXISTS events (
                        event_id TEXT PRIMARY KEY,
                        node_id TEXT NOT NULL,
                        budget_epoch TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        entity_id TEXT NOT NULL,
                        event_version INTEGER NOT NULL CHECK(event_version >= 1),
                        created_at TEXT NOT NULL,
                        tombstone INTEGER NOT NULL DEFAULT 0 CHECK(tombstone IN (0, 1)),
                        dedupe_key TEXT UNIQUE,
                        payload_json TEXT NOT NULL,
                        payload_hash TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_events_epoch
                        ON events(budget_epoch, event_type);
                    CREATE INDEX IF NOT EXISTS idx_events_entity
                        ON events(entity_type, entity_id, event_version);
                    INSERT OR IGNORE INTO schema_migrations(version, applied_at)
                        VALUES (1, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));
                    PRAGMA user_version=1;
                    COMMIT;
                    """
                )

    @contextmanager
    def immediate(self) -> Iterator[sqlite3.Connection]:
        conn = self.connect()
        try:
            conn.execute("BEGIN IMMEDIATE")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def append(
        self,
        *,
        node_id: str,
        budget_epoch: str,
        event_type: str,
        entity_type: str,
        entity_id: str,
        payload: dict[str, Any],
        event_version: int = 1,
        tombstone: bool = False,
        dedupe_key: str | None = None,
        event_id: str | None = None,
        created_at: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> Event:
        event = Event(
            event_id=event_id or new_event_id(),
            node_id=node_id,
            budget_epoch=budget_epoch,
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            event_version=event_version,
            created_at=created_at or utc_now(),
            tombstone=tombstone,
            dedupe_key=dedupe_key,
            payload=payload,
            payload_hash=content_hash(payload),
        )
        owns_connection = connection is None
        conn = connection or self.connect()
        try:
            if owns_connection:
                conn.execute("BEGIN IMMEDIATE")
            self._insert_or_compare(conn, event)
            if owns_connection:
                conn.commit()
        except Exception:
            if owns_connection:
                conn.rollback()
            raise
        finally:
            if owns_connection:
                conn.close()
        stored = self.get(event_id=event.event_id, connection=connection)
        if stored is None and event.dedupe_key:
            stored = self.get(dedupe_key=event.dedupe_key, connection=connection)
        return stored or event

    def _insert_or_compare(self, conn: sqlite3.Connection, event: Event) -> None:
        try:
            conn.execute(
                """
                INSERT INTO events(
                    event_id, node_id, budget_epoch, event_type, entity_type, entity_id,
                    event_version, created_at, tombstone, dedupe_key, payload_json, payload_hash
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.node_id,
                    event.budget_epoch,
                    event.event_type,
                    event.entity_type,
                    event.entity_id,
                    event.event_version,
                    event.created_at,
                    int(event.tombstone),
                    event.dedupe_key,
                    canonical_json(event.payload),
                    event.payload_hash,
                ),
            )
        except sqlite3.IntegrityError as exc:
            existing = conn.execute(
                "SELECT * FROM events WHERE event_id=? OR (? IS NOT NULL AND dedupe_key=?)",
                (event.event_id, event.dedupe_key, event.dedupe_key),
            ).fetchone()
            if existing is None:
                raise
            stored = Event.from_row(existing)
            comparable = (
                stored.node_id,
                stored.budget_epoch,
                stored.event_type,
                stored.entity_type,
                stored.entity_id,
                stored.event_version,
                stored.tombstone,
                stored.dedupe_key,
                stored.payload_hash,
            )
            incoming = (
                event.node_id,
                event.budget_epoch,
                event.event_type,
                event.entity_type,
                event.entity_id,
                event.event_version,
                event.tombstone,
                event.dedupe_key,
                event.payload_hash,
            )
            if comparable != incoming:
                raise EventConflictError(
                    f"event identity conflict for {event.event_id}/{event.dedupe_key}"
                ) from exc

    def get(
        self,
        *,
        event_id: str | None = None,
        dedupe_key: str | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> Event | None:
        if not event_id and not dedupe_key:
            raise ValueError("event_id or dedupe_key is required")
        owns_connection = connection is None
        conn = connection or self.connect()
        try:
            if event_id:
                row = conn.execute("SELECT * FROM events WHERE event_id=?", (event_id,)).fetchone()
            else:
                row = conn.execute(
                    "SELECT * FROM events WHERE dedupe_key=?", (dedupe_key,)
                ).fetchone()
            return Event.from_row(row) if row else None
        finally:
            if owns_connection:
                conn.close()

    def events(
        self,
        *,
        budget_epoch: str | None = None,
        event_types: Sequence[str] | None = None,
        connection: sqlite3.Connection | None = None,
    ) -> list[Event]:
        owns_connection = connection is None
        conn = connection or self.connect()
        clauses: list[str] = []
        params: list[Any] = []
        if budget_epoch is not None:
            clauses.append("budget_epoch=?")
            params.append(budget_epoch)
        if event_types:
            clauses.append(f"event_type IN ({','.join('?' for _ in event_types)})")
            params.extend(event_types)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        try:
            rows = conn.execute(
                f"SELECT * FROM events{where} ORDER BY event_id", params
            ).fetchall()
            return [Event.from_row(row) for row in rows]
        finally:
            if owns_connection:
                conn.close()

    def import_events(self, events: Sequence[Event | dict[str, Any]]) -> int:
        inserted_before = self.count()
        with self.immediate() as conn:
            for value in events:
                event = value if isinstance(value, Event) else Event(
                    event_id=value["event_id"],
                    node_id=value["node_id"],
                    budget_epoch=value["budget_epoch"],
                    event_type=value["event_type"],
                    entity_type=value["entity_type"],
                    entity_id=value["entity_id"],
                    event_version=int(value["event_version"]),
                    created_at=value["created_at"],
                    tombstone=bool(value.get("tombstone", False)),
                    dedupe_key=value.get("dedupe_key"),
                    payload=dict(value["payload"]),
                    payload_hash=value.get("payload_hash") or content_hash(value["payload"]),
                )
                if event.payload_hash != content_hash(event.payload):
                    raise EventConflictError(f"payload hash mismatch for {event.event_id}")
                self._insert_or_compare(conn, event)
        return self.count() - inserted_before

    def count(self) -> int:
        with self.connect() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM events").fetchone()[0])

    def schema_version(self) -> int:
        with self.connect() as conn:
            return int(conn.execute("PRAGMA user_version").fetchone()[0])
