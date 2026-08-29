from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from automation_master.runtime import (
    AutomationRuntime,
    RuntimeReceiptConflictError,
    RuntimeReceiptStore,
    read_provider_receipt,
    read_scheduler_run,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SHA_A = "a" * 64
SHA_B = "b" * 64
SHA_C = "c" * 64
SHA_D = "d" * 64
SHA_E = "e" * 64


def authority(input_kind: str, precedence: str, digest: str) -> dict[str, str]:
    return {
        "input_kind": input_kind,
        "authority_id": f"authority:{input_kind}",
        "scope": "automation:daily-briefing",
        "resolved_uri": f"authority://{input_kind}/current",
        "content_sha256": digest,
        "observed_at": "2026-08-29T09:59:00+02:00",
        "precedence": precedence,
    }


def receipt_payload(receipt_id: str = "run-20260829-001") -> dict:
    return {
        "receipt_id": receipt_id,
        "automation_id": "daily-briefing",
        "definition_version": "git:0123456789abcdef0123456789abcdef01234567",
        "origin_system": "ASUS-GEI",
        "provider": "codex-automation",
        "execution_class": "pinned-runtime-release",
        "execution_pin": "0123456789abcdef0123456789abcdef01234567",
        "scheduled_for": "2026-08-29T10:00:00+02:00",
        "started_at": "2026-08-29T10:00:03+02:00",
        "finished_at": "2026-08-29T10:00:11+02:00",
        "status": "succeeded",
        "authority_resolution": [
            authority("rules", "explicit-policy-and-rule", SHA_A),
            authority("policies", "explicit-policy-and-rule", SHA_B),
            authority("decisions", "project-user-decision", SHA_C),
            authority("workflows", "workflow-contract", SHA_D),
            authority("approved-user-preferences", "approved-user-preference", SHA_E),
        ],
        "input_fingerprints": {
            "definition_sha256": SHA_A,
            "input_envelope_sha256": SHA_B,
        },
        "output_summary": {
            "result": "completed",
            "items_processed": 3,
        },
        "mutation_class": "read-only-redundant",
        "rollback_ref": None,
        "provider_readback": {
            "source_kind": "provider",
            "source_id": "codex-automation",
            "native_receipt_id": "provider-run-001",
            "observed_at": "2026-08-29T10:00:12+02:00",
            "status": "succeeded",
            "content_sha256": SHA_C,
        },
        "scheduler_readback": {
            "source_kind": "scheduler",
            "source_id": "codex-scheduler",
            "native_receipt_id": "scheduler-attempt-001",
            "observed_at": "2026-08-29T10:00:13+02:00",
            "status": "succeeded",
            "content_sha256": SHA_D,
        },
    }


def test_runtime_records_closed_receipt_from_native_readbacks(tmp_path: Path):
    runtime = AutomationRuntime(RuntimeReceiptStore(tmp_path / "receipts"))

    receipt = runtime.record(receipt_payload())

    assert receipt["schema"] == "ellmos.automation-runtime-receipt.v1"
    assert receipt["receipt_id"] == "run-20260829-001"
    assert len(receipt["content_sha256"]) == 64
    assert receipt["provider_readback"]["native_receipt_id"] == "provider-run-001"
    assert receipt["scheduler_readback"]["native_receipt_id"] == "scheduler-attempt-001"
    assert {item["input_kind"] for item in receipt["authority_resolution"]} == {
        "rules",
        "policies",
        "decisions",
        "workflows",
        "approved-user-preferences",
    }
    stored = json.loads((tmp_path / "receipts" / "run-20260829-001.json").read_text("utf-8"))
    assert stored == receipt


def test_runtime_receipts_are_idempotent_immutable_and_statistics_are_bounded(tmp_path: Path):
    runtime = AutomationRuntime(RuntimeReceiptStore(tmp_path / "receipts"))
    first = runtime.record(receipt_payload())
    second = runtime.record(receipt_payload())
    assert second == first

    conflicting = receipt_payload()
    conflicting["output_summary"]["items_processed"] = 4
    with pytest.raises(RuntimeReceiptConflictError, match="immutable receipt conflict"):
        runtime.record(conflicting)

    failed = receipt_payload("run-20260829-002")
    failed["status"] = "failed"
    failed["provider_readback"]["native_receipt_id"] = "provider-run-002"
    failed["scheduler_readback"]["native_receipt_id"] = "scheduler-attempt-002"
    runtime.record(failed)

    statistics = runtime.statistics()
    assert statistics == {
        "schema": "ellmos.automation-runtime-statistics.v1",
        "receipt_count": 2,
        "by_status": {"failed": 1, "succeeded": 1},
        "latest_finished_at": "2026-08-29T10:00:11+02:00",
    }
    assert "output_summary" not in statistics
    assert "automation_id" not in statistics


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda value: value.pop("scheduler_readback"), "scheduler_readback"),
        (
            lambda value: value["authority_resolution"].pop(),
            "authority input coverage",
        ),
        (
            lambda value: value["output_summary"].update(
                {"raw_prompt_content": "summarise private inbox"}
            ),
            "raw or secret field",
        ),
        (
            lambda value: value["output_summary"].update(
                {"diagnostic": "password=hunter2-secret-value"}
            ),
            "credential or secret",
        ),
        (
            lambda value: value["input_fingerprints"].update(
                {"raw_input": "private payload"}
            ),
            "fingerprint",
        ),
        (
            lambda value: value.update({"execution_pin": "main"}),
            "immutable execution_pin",
        ),
    ],
)
def test_runtime_fails_closed_on_missing_authority_or_sensitive_payload(
    tmp_path: Path, mutate, message: str
):
    payload = receipt_payload()
    mutate(payload)

    with pytest.raises(ValueError, match=message):
        AutomationRuntime(RuntimeReceiptStore(tmp_path / "receipts")).record(payload)


def test_runtime_rejects_cloud_synced_receipt_root(tmp_path: Path, monkeypatch):
    onedrive = tmp_path / "OneDrive"
    monkeypatch.setenv("OneDrive", str(onedrive))

    with pytest.raises(ValueError, match="cloud-synced"):
        RuntimeReceiptStore(onedrive / "automation-runtime" / "receipts")


def test_runtime_cli_records_and_reports_without_creating_governance_db(tmp_path: Path):
    input_path = tmp_path / "receipt.json"
    input_path.write_text(json.dumps(receipt_payload()), encoding="utf-8")
    receipt_root = tmp_path / "receipts"
    db_path = tmp_path / "must-not-exist.db"
    command = [
        sys.executable,
        "-m",
        "automation_master",
        "--db",
        str(db_path),
        "--receipts-dir",
        str(receipt_root),
    ]
    env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}

    recorded = subprocess.run(
        [*command, "runtime-record", str(input_path)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    assert recorded.returncode == 0, recorded.stderr
    assert json.loads(recorded.stdout)["receipt_id"] == "run-20260829-001"
    assert not db_path.exists()

    stats = subprocess.run(
        [*command, "runtime-stats"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    assert stats.returncode == 0, stats.stderr
    assert json.loads(stats.stdout)["receipt_count"] == 1
    assert not db_path.exists()

    provider_native = tmp_path / "provider-native.json"
    provider_native.write_text(
        json.dumps(
            {
                "receipt_id": "provider-native-1",
                "status": "succeeded",
                "finished_at": "2026-08-29T10:00:11+02:00",
                "raw_prompt": "not exported",
            }
        ),
        encoding="utf-8",
    )
    readback = subprocess.run(
        [
            *command,
            "runtime-provider-readback",
            str(provider_native),
            "--source-id",
            "codex-automation",
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
    )
    assert readback.returncode == 0, readback.stderr
    assert json.loads(readback.stdout)["native_receipt_id"] == "provider-native-1"
    assert "raw_prompt" not in readback.stdout
    assert not db_path.exists()


def test_runtime_rejects_unknown_fields(tmp_path: Path):
    payload = deepcopy(receipt_payload())
    payload["provider_mutation"] = "enable"

    with pytest.raises(ValueError, match="unsupported receipt fields"):
        AutomationRuntime(RuntimeReceiptStore(tmp_path / "receipts")).record(payload)


def test_runtime_detects_tampered_stored_receipt(tmp_path: Path):
    runtime = AutomationRuntime(RuntimeReceiptStore(tmp_path / "receipts"))
    runtime.record(receipt_payload())
    target = tmp_path / "receipts" / "run-20260829-001.json"
    stored = json.loads(target.read_text(encoding="utf-8"))
    stored["status"] = "failed"
    target.write_text(json.dumps(stored), encoding="utf-8")

    with pytest.raises(ValueError, match="content hash mismatch"):
        runtime.statistics()


def test_provider_native_readback_returns_only_hashed_metadata(tmp_path: Path):
    source = tmp_path / "provider-receipt.json"
    source.write_text(
        json.dumps(
            {
                "receipt_id": "provider-native-1",
                "status": "succeeded",
                "finished_at": "2026-08-29T10:00:11+02:00",
                "raw_prompt": "private source text",
                "token": "secret-value-that-must-not-leak",
            }
        ),
        encoding="utf-8",
    )

    readback = read_provider_receipt(source, source_id="codex-automation")

    assert readback["source_kind"] == "provider"
    assert readback["native_receipt_id"] == "provider-native-1"
    assert readback["status"] == "succeeded"
    assert len(readback["content_sha256"]) == 64
    assert "raw_prompt" not in readback
    assert "token" not in readback
    assert str(source) not in json.dumps(readback)


def test_scheduler_native_readback_is_sqlite_read_only_and_bounded(tmp_path: Path):
    database = tmp_path / "scheduler.db"
    with sqlite3.connect(database) as connection:
        connection.execute(
            """
            CREATE TABLE runs (
                run_id TEXT PRIMARY KEY,
                job_id TEXT NOT NULL,
                scheduled_for TEXT NOT NULL,
                attempt INTEGER NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                output TEXT NOT NULL,
                error TEXT NOT NULL,
                authority_set_sha256 TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "scheduler-run-1",
                "daily-briefing",
                "2026-08-29T08:00:00Z",
                1,
                "succeeded",
                "2026-08-29T08:00:03Z",
                "2026-08-29T08:00:11Z",
                "raw private output",
                "password=must-not-leak",
                SHA_A,
            ),
        )
    before = database.read_bytes()

    readback = read_scheduler_run(database, "scheduler-run-1")

    assert database.read_bytes() == before
    assert readback["source_kind"] == "scheduler"
    assert readback["source_id"] == "ellmos-scheduler"
    assert readback["native_receipt_id"] == "scheduler-run-1"
    assert readback["status"] == "succeeded"
    assert len(readback["content_sha256"]) == 64
    assert "output" not in readback
    assert "error" not in readback
    assert str(database) not in json.dumps(readback)


def test_scheduler_readback_fails_closed_on_unknown_schema(tmp_path: Path):
    database = tmp_path / "not-scheduler.db"
    with sqlite3.connect(database) as connection:
        connection.execute("CREATE TABLE unrelated (id TEXT PRIMARY KEY)")

    with pytest.raises(ValueError, match="scheduler runs schema"):
        read_scheduler_run(database, "missing")
