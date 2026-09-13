"""Small operational CLI; it never starts automation processes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

from . import __version__
from .models import AutomationSpec, MutationClass, RewardSignals, RunClass
from .reward import RewardPolicy
from .service import AutomationMaster
from .store import EventStore


def default_db_path() -> Path:
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return base / "ellmos" / "automation-master" / "automation-master.db"


def _emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="automation-master",
        description="Local-first automation credit governance.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument("--db", type=Path, default=default_db_path())
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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
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


if __name__ == "__main__":
    raise SystemExit(main())
