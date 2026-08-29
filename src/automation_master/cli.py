"""Small operational CLI; it never starts automation processes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from .models import AutomationSpec, MutationClass, RewardSignals, RunClass
from .reward import RewardPolicy
from .runtime import (
    AutomationRuntime,
    RuntimeReceiptStore,
    read_provider_receipt,
    read_scheduler_run,
)
from .service import AutomationMaster
from .store import EventStore


def default_db_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "ellmos" / "automation-master" / "automation-master.db"


def default_receipts_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "ellmos" / "automation-master" / "automation-runtime" / "receipts"


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="automation-master",
        description="Local-first automation credit governance.",
    )
    parser.add_argument("--db", type=Path, default=default_db_path())
    parser.add_argument("--receipts-dir", type=Path, default=default_receipts_path())
    parser.add_argument("--node", default=os.environ.get("AUTOMATION_MASTER_NODE", "local"))
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("init")
    status = commands.add_parser("status")
    status.add_argument("--epoch")
    status.add_argument("--scope")

    family = commands.add_parser("register-family")
    family.add_argument("family_id")
    family.add_argument("name")
    family.add_argument("--version", type=int, default=1)

    automation = commands.add_parser("register-automation")
    automation.add_argument("automation_id")
    automation.add_argument("family_id")
    automation.add_argument("variant_id")
    automation.add_argument(
        "--mutation-class",
        type=MutationClass,
        choices=list(MutationClass),
        default=MutationClass.READ_ONLY_REDUNDANT,
    )
    automation.add_argument(
        "--run-class",
        type=RunClass,
        choices=list(RunClass),
        default=RunClass.COMPARABLE,
    )
    automation.add_argument("--version", type=int, default=1)

    allocation = commands.add_parser("allocate")
    allocation.add_argument("epoch")
    allocation.add_argument("scope")
    allocation.add_argument("credits", type=int)
    allocation.add_argument("allocation_id")

    reward = commands.add_parser("reward")
    for name in (
        "current_interest",
        "coverage_gap",
        "deadline_pressure",
        "utility",
        "cost_per_useful_result",
        "no_work_rate",
        "error_rate",
        "redundancy",
        "independent_review_value",
    ):
        reward.add_argument(f"--{name.replace('_', '-')}", type=float, default=0.0)
    reward.add_argument("--stale-epochs", type=int, default=0)
    reward.add_argument("--previous-score", type=float)
    runtime_record = commands.add_parser("runtime-record")
    runtime_record.add_argument("receipt", type=Path)
    commands.add_parser("runtime-stats")
    provider_readback = commands.add_parser("runtime-provider-readback")
    provider_readback.add_argument("receipt", type=Path)
    provider_readback.add_argument("--source-id", required=True)
    provider_readback.add_argument("--receipt-id-field", default="receipt_id")
    provider_readback.add_argument("--status-field", default="status")
    provider_readback.add_argument("--observed-at-field", default="finished_at")
    scheduler_readback = commands.add_parser("runtime-scheduler-readback")
    scheduler_readback.add_argument("database", type=Path)
    scheduler_readback.add_argument("run_id")
    scheduler_readback.add_argument("--source-id", default="ellmos-scheduler")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "runtime-provider-readback":
        _emit(
            read_provider_receipt(
                args.receipt,
                source_id=args.source_id,
                receipt_id_field=args.receipt_id_field,
                status_field=args.status_field,
                observed_at_field=args.observed_at_field,
            )
        )
        return 0
    if args.command == "runtime-scheduler-readback":
        _emit(
            read_scheduler_run(
                args.database,
                args.run_id,
                source_id=args.source_id,
            )
        )
        return 0
    if args.command in {"runtime-record", "runtime-stats"}:
        runtime = AutomationRuntime(RuntimeReceiptStore(args.receipts_dir))
        if args.command == "runtime-record":
            payload = json.loads(args.receipt.read_text(encoding="utf-8"))
            _emit(runtime.record(payload))
        else:
            _emit(runtime.statistics())
        return 0
    store = EventStore(args.db)
    master = AutomationMaster(store, node_id=args.node)
    if args.command == "init":
        _emit({"database": str(store.path), "schema_version": store.schema_version()})
    elif args.command == "status":
        result: dict[str, Any] = {
            "database": str(store.path),
            "schema_version": store.schema_version(),
            "event_count": store.count(),
            "registry": master.registry(),
        }
        if args.epoch and args.scope:
            result["budget"] = master.budget_state(args.epoch, args.scope).as_dict()
        _emit(result)
    elif args.command == "register-family":
        _emit(
            master.register_family(
                args.family_id,
                name=args.name,
                version=args.version,
            ).as_dict()
        )
    elif args.command == "register-automation":
        spec = AutomationSpec(
            automation_id=args.automation_id,
            family_id=args.family_id,
            variant_id=args.variant_id,
            mutation_class=args.mutation_class,
            run_class=args.run_class,
            version=args.version,
        )
        _emit(master.register_automation(spec).as_dict())
    elif args.command == "allocate":
        _emit(
            master.allocate_budget(
                budget_epoch=args.epoch,
                scope_id=args.scope,
                credits=args.credits,
                allocation_id=args.allocation_id,
            ).as_dict()
        )
    elif args.command == "reward":
        values = vars(args)
        signal_names = RewardSignals.__dataclass_fields__.keys()
        signals = RewardSignals(**{name: values[name] for name in signal_names})
        _emit(RewardPolicy().score(signals, previous_score=args.previous_score).as_dict())
    return 0
