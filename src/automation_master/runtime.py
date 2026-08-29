"""Fail-closed automation runtime observation and immutable receipt storage.

This module observes evidence supplied by provider-native and scheduler-native
readbacks.  It never schedules a run, launches a provider, changes provider
state, or derives authority from runtime data.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sqlite3
from collections import Counter
from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import MutationClass, canonical_json, content_hash
from .security import require_export_safe

RECEIPT_SCHEMA = "ellmos.automation-runtime-receipt.v1"
STATISTICS_SCHEMA = "ellmos.automation-runtime-statistics.v1"

_RECEIPT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_IMMUTABLE_PIN_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64}|sha256:[0-9a-f]{64})$")
_INPUT_FIELDS = {
    "receipt_id",
    "automation_id",
    "definition_version",
    "origin_system",
    "provider",
    "execution_class",
    "execution_pin",
    "scheduled_for",
    "started_at",
    "finished_at",
    "status",
    "authority_resolution",
    "input_fingerprints",
    "output_summary",
    "mutation_class",
    "rollback_ref",
    "provider_readback",
    "scheduler_readback",
}
_READBACK_FIELDS = {
    "source_kind",
    "source_id",
    "native_receipt_id",
    "observed_at",
    "status",
    "content_sha256",
}
_AUTHORITY_FIELDS = {
    "input_kind",
    "authority_id",
    "scope",
    "resolved_uri",
    "content_sha256",
    "observed_at",
    "precedence",
}
_REQUIRED_AUTHORITY_INPUTS = {
    "rules",
    "policies",
    "decisions",
    "workflows",
    "approved-user-preferences",
}
_PRECEDENCE = {
    "project-user-decision",
    "global-user-decision",
    "explicit-policy-and-rule",
    "validated-predicted/delegated-avatar-decision",
    "approved-user-preference",
    "workflow-contract",
    "raw-derived-user-model-non-authorizing",
}
_EXECUTION_CLASSES = {
    "app-native",
    "pinned-runtime-release",
    "dedicated-runtime-checkout",
    "development-worktree-only",
}
_STATUSES = {"succeeded", "failed", "blocked", "suppressed", "skipped", "stale"}
_RAW_OR_SECRET_KEYS = {
    "raw_prompt",
    "raw_prompt_content",
    "raw_personal_payload",
    "personal_payload",
    "secret",
    "secret_value",
    "secret_values",
    "password",
    "token",
    "api_key",
    "credential_path",
}


class RuntimeReceiptConflictError(RuntimeError):
    """A receipt ID already exists with different immutable content."""


class RuntimeReceiptStore:
    """Host-local, create-only JSON store for automation runtime receipts."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).expanduser().resolve(strict=False)
        _reject_cloud_synced_root(self.root)
        self.root.mkdir(parents=True, exist_ok=True)

    def record(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        receipt = build_runtime_receipt(payload)
        target = self.root / f"{receipt['receipt_id']}.json"
        encoded = json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        try:
            with target.open("x", encoding="utf-8", newline="\n") as handle:
                handle.write(encoded)
        except FileExistsError:
            existing = self._read(target)
            if existing != receipt:
                raise RuntimeReceiptConflictError(
                    f"immutable receipt conflict for {receipt['receipt_id']}"
                ) from None
            return existing
        return receipt

    def receipts(self) -> list[dict[str, Any]]:
        return [self._read(path) for path in sorted(self.root.glob("*.json"))]

    @staticmethod
    def _read(path: Path) -> dict[str, Any]:
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"runtime receipt is unreadable: {path}") from exc
        if not isinstance(value, dict) or value.get("schema") != RECEIPT_SCHEMA:
            raise ValueError(f"runtime receipt has an unsupported schema: {path}")
        declared_hash = value.get("content_sha256")
        unsigned = dict(value)
        unsigned.pop("content_sha256", None)
        if declared_hash != content_hash(unsigned):
            raise ValueError(f"runtime receipt content hash mismatch: {path}")
        return value


class AutomationRuntime:
    """Readback consumer for the logical ``module:automation-runtime`` role."""

    def __init__(self, store: RuntimeReceiptStore) -> None:
        self.store = store

    def record(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        return self.store.record(payload)

    def statistics(self) -> dict[str, Any]:
        receipts = self.store.receipts()
        counts = Counter(receipt["status"] for receipt in receipts)
        latest = max(
            receipts,
            key=lambda receipt: _parse_timestamp(receipt["finished_at"], "finished_at"),
            default=None,
        )
        return {
            "schema": STATISTICS_SCHEMA,
            "receipt_count": len(receipts),
            "by_status": dict(sorted(counts.items())),
            "latest_finished_at": latest["finished_at"] if latest else None,
        }


def read_provider_receipt(
    path: str | Path,
    *,
    source_id: str,
    receipt_id_field: str = "receipt_id",
    status_field: str = "status",
    observed_at_field: str = "finished_at",
) -> dict[str, Any]:
    """Read one provider-native JSON receipt without projecting its payload."""

    source = Path(path).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("provider receipt must be a regular non-symlink file")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("provider source_id must be non-empty")
    for name, selector in {
        "receipt_id_field": receipt_id_field,
        "status_field": status_field,
        "observed_at_field": observed_at_field,
    }.items():
        if not isinstance(selector, str) or not selector.strip():
            raise ValueError(f"{name} must be non-empty")
    raw = source.read_bytes()
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError("provider receipt exceeds the 4 MiB readback bound")
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("provider receipt is not valid UTF-8 JSON") from exc
    if not isinstance(value, Mapping):
        raise ValueError("provider receipt must contain a JSON object")
    receipt_id = value.get(receipt_id_field)
    status = value.get(status_field)
    observed_at = value.get(observed_at_field)
    if not isinstance(receipt_id, str) or not receipt_id.strip():
        raise ValueError("provider native receipt ID is missing")
    if not isinstance(status, str) or not status.strip():
        raise ValueError("provider native status is missing")
    _parse_timestamp(observed_at, "provider native observed_at")
    return {
        "source_kind": "provider",
        "source_id": source_id,
        "native_receipt_id": receipt_id,
        "observed_at": observed_at,
        "status": status,
        "content_sha256": hashlib.sha256(raw).hexdigest(),
    }


def read_scheduler_run(
    database: str | Path,
    run_id: str,
    *,
    source_id: str = "ellmos-scheduler",
) -> dict[str, Any]:
    """Read a bounded ellmos-scheduler run through an immutable SQLite handle."""

    source = Path(database).expanduser()
    if source.is_symlink() or not source.is_file():
        raise ValueError("scheduler database must be a regular non-symlink file")
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("scheduler run_id must be non-empty")
    if not isinstance(source_id, str) or not source_id.strip():
        raise ValueError("scheduler source_id must be non-empty")
    wal_path = source.with_name(f"{source.name}-wal")
    if wal_path.exists() and wal_path.stat().st_size:
        raise ValueError(
            "scheduler database has a live WAL; use a scheduler-native closed snapshot"
        )

    required_columns = {
        "run_id",
        "job_id",
        "scheduled_for",
        "attempt",
        "status",
        "started_at",
        "finished_at",
        "authority_set_sha256",
    }
    uri = f"{source.resolve(strict=True).as_uri()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
    except sqlite3.Error as exc:
        raise ValueError("scheduler database could not be opened read-only") from exc
    connection.row_factory = sqlite3.Row
    try:
        columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(runs)").fetchall()
        }
        if not required_columns.issubset(columns):
            raise ValueError("scheduler runs schema is missing required columns")
        row = connection.execute(
            """
            SELECT run_id, job_id, scheduled_for, attempt, status,
                   started_at, finished_at, authority_set_sha256
            FROM runs WHERE run_id = ?
            """,
            (run_id,),
        ).fetchone()
    except sqlite3.Error as exc:
        raise ValueError("scheduler runs schema could not be read") from exc
    finally:
        connection.close()
    if row is None:
        raise ValueError("scheduler run_id was not found")
    safe_row = dict(row)
    observed_at = (
        safe_row.get("finished_at")
        or safe_row.get("started_at")
        or safe_row.get("scheduled_for")
    )
    _parse_timestamp(observed_at, "scheduler native observed_at")
    return {
        "source_kind": "scheduler",
        "source_id": source_id,
        "native_receipt_id": safe_row["run_id"],
        "observed_at": observed_at,
        "status": safe_row["status"],
        "content_sha256": content_hash(safe_row),
    }


def build_runtime_receipt(payload: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ValueError("runtime receipt payload must be an object")
    unsupported = set(payload) - _INPUT_FIELDS
    missing = _INPUT_FIELDS - set(payload)
    if unsupported or missing:
        raise ValueError(
            "unsupported receipt fields or missing required fields: "
            f"unsupported={sorted(unsupported)}, missing={sorted(missing)}"
        )

    value = deepcopy(dict(payload))
    receipt_id = _required_string(value, "receipt_id")
    if not _RECEIPT_ID_RE.fullmatch(receipt_id):
        raise ValueError("receipt_id must be a portable file-safe identifier")
    for name in (
        "automation_id",
        "definition_version",
        "origin_system",
        "provider",
        "execution_pin",
    ):
        _required_string(value, name)
    if value["execution_class"] not in _EXECUTION_CLASSES:
        raise ValueError("execution_class is unsupported")
    if (
        value["execution_class"] != "app-native"
        and not _IMMUTABLE_PIN_RE.fullmatch(value["execution_pin"])
    ):
        raise ValueError("non-app-native runs require an immutable execution_pin")
    if value["status"] not in _STATUSES:
        raise ValueError("status is unsupported")
    if value["mutation_class"] not in {member.value for member in MutationClass}:
        raise ValueError("mutation_class is unsupported")
    rollback_ref = value["rollback_ref"]
    if rollback_ref is not None and (
        not isinstance(rollback_ref, str) or not rollback_ref.strip()
    ):
        raise ValueError("rollback_ref must be null or a non-empty stable reference")

    _parse_timestamp(value["scheduled_for"], "scheduled_for")
    started = _parse_timestamp(value["started_at"], "started_at")
    finished = _parse_timestamp(value["finished_at"], "finished_at")
    if finished < started:
        raise ValueError("finished_at must not precede started_at")

    _validate_readback(value["provider_readback"], "provider")
    _validate_readback(value["scheduler_readback"], "scheduler")
    _validate_authorities(value["authority_resolution"])
    _validate_fingerprints(value["input_fingerprints"])
    _validate_output_summary(value["output_summary"])
    _reject_raw_or_secret_fields(value)
    try:
        require_export_safe(value)
    except ValueError as exc:
        raise ValueError("runtime receipt resembles a credential or secret") from exc

    receipt = {"schema": RECEIPT_SCHEMA, **value}
    receipt["content_sha256"] = content_hash(receipt)
    return receipt


def _validate_readback(value: Any, expected_kind: str) -> None:
    if not isinstance(value, Mapping) or set(value) != _READBACK_FIELDS:
        raise ValueError(f"{expected_kind}_readback fields are not closed")
    if value.get("source_kind") != expected_kind:
        raise ValueError(f"{expected_kind}_readback source_kind mismatch")
    for field in ("source_id", "native_receipt_id", "status"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ValueError(f"{expected_kind}_readback {field} must be non-empty")
    _parse_timestamp(value.get("observed_at"), f"{expected_kind}_readback.observed_at")
    _require_sha256(value.get("content_sha256"), f"{expected_kind}_readback.content_sha256")


def _validate_authorities(value: Any) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("authority_resolution must be a non-empty list")
    kinds: list[str] = []
    for item in value:
        if not isinstance(item, Mapping) or set(item) != _AUTHORITY_FIELDS:
            raise ValueError("authority_resolution fields are not closed")
        kind = item.get("input_kind")
        if kind not in _REQUIRED_AUTHORITY_INPUTS:
            raise ValueError("authority_resolution input_kind is unsupported")
        kinds.append(kind)
        for field in ("authority_id", "scope", "resolved_uri"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                raise ValueError(f"authority_resolution {field} must be non-empty")
        _require_sha256(item.get("content_sha256"), "authority_resolution.content_sha256")
        _parse_timestamp(item.get("observed_at"), "authority_resolution.observed_at")
        if item.get("precedence") not in _PRECEDENCE:
            raise ValueError("authority_resolution precedence is unsupported")
    if len(kinds) != len(set(kinds)) or set(kinds) != _REQUIRED_AUTHORITY_INPUTS:
        raise ValueError("authority input coverage must contain each required input exactly once")


def _validate_fingerprints(value: Any) -> None:
    if not isinstance(value, Mapping) or not value:
        raise ValueError("input_fingerprints must be a non-empty object")
    for name, digest in value.items():
        if not isinstance(name, str) or not name.endswith("_sha256"):
            raise ValueError("input fingerprint keys must end in _sha256")
        _require_sha256(digest, f"input fingerprint {name}")


def _validate_output_summary(value: Any) -> None:
    if not isinstance(value, Mapping):
        raise ValueError("output_summary must be an object")
    _reject_raw_or_secret_fields(value)
    try:
        require_export_safe(value)
    except ValueError as exc:
        raise ValueError("output_summary resembles a credential or secret") from exc
    if len(canonical_json(value).encode("utf-8")) > 4096:
        raise ValueError("output_summary exceeds the 4096-byte bound")


def _reject_raw_or_secret_fields(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            normalized = str(key).strip().casefold().replace("-", "_")
            if normalized in _RAW_OR_SECRET_KEYS:
                raise ValueError("output_summary contains a raw or secret field")
            _reject_raw_or_secret_fields(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_raw_or_secret_fields(item)


def _required_string(value: Mapping[str, Any], name: str) -> str:
    item = value.get(name)
    if not isinstance(item, str) or not item.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return item


def _require_sha256(value: Any, name: str) -> None:
    if not isinstance(value, str) or not _SHA256_RE.fullmatch(value):
        raise ValueError(f"{name} must be a lowercase SHA-256 digest")


def _parse_timestamp(value: Any, name: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty ISO timestamp")
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = f"{normalized[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ValueError(f"{name} must be a valid ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"{name} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _reject_cloud_synced_root(root: Path) -> None:
    for variable in ("OneDrive", "OneDriveConsumer", "OneDriveCommercial"):
        configured = os.environ.get(variable)
        if not configured:
            continue
        cloud_root = Path(configured).expanduser().resolve(strict=False)
        if root == cloud_root or root.is_relative_to(cloud_root):
            raise ValueError("automation runtime receipts cannot use a cloud-synced root")


__all__ = [
    "AutomationRuntime",
    "RuntimeReceiptConflictError",
    "RuntimeReceiptStore",
    "build_runtime_receipt",
    "read_provider_receipt",
    "read_scheduler_run",
]
