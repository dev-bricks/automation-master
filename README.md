# automation-master

<img src="banner.png" width="100%" alt="automation-master banner">

[![Pytest](https://img.shields.io/badge/pytest-45%20passed-brightgreen.svg)](https://pytest.org)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ecosystem: dev-bricks](https://img.shields.io/badge/Ecosystem-dev--bricks-blue.svg)](https://github.com/dev-bricks)
[![Umbrella: open-bricks](https://img.shields.io/badge/Umbrella-open--bricks-purple.svg)](https://github.com/open-bricks)
[![LLM-Ready](https://img.shields.io/badge/LLM--Ready-llms.txt-blue.svg)](llms.txt)

> [!NOTE]
> Quick index for LLMs and AI coding agents: see [llms.txt](llms.txt) for context, boundaries, and API signatures.

`automation-master` is a private-by-default, local-first control module for
scheduled automation families. It registers comparable variants, calculates
explainable reward scores, assigns epoch-scoped credit envelopes, records run
receipts, and proposes throttling inputs.

It does **not** schedule processes, start jobs, replace `task-master`, or replace
`ticket-master`. Integration with `ellmos-scheduler`, `system-gap-master`, and
`sqlite-transit-sync` happens through narrow adapters.

## Architecture

```mermaid
graph TD
    subgraph ExternalClients ["External Callers & Schedulers"]
        SCHED["ellmos-scheduler / Cron"]
        GAP["system-gap-master"]
        TRANSIT["sqlite-transit-sync"]
    end

    subgraph Adapters ["Narrow Adapter Seams"]
        GATE["CreditGateAdapter<br/>(Preflight & Authorization)"]
        DEP["DeploymentPlan Validator<br/>(Discovery & Health)"]
        SYNC["ImmutableMergePolicy<br/>(Append-Only Union)"]
        PROMPT["PromptRepairContract<br/>(Antigravity Invariant Guard)"]
    end

    subgraph CoreEngine ["automation-master Core Engine"]
        SVC["AutomationMaster Service"]
        POLICY["RewardPolicy<br/>(Deterministic Scoring)"]
        CREDIT["CreditPolicy<br/>(SHADOW / ENFORCED)"]
        RETENTION["ReceiptRetentionPolicy<br/>(30d Detailed & Audit Summary)"]
    end

    subgraph Storage ["Local-First Event Storage"]
        LEDGER[("SQLite Event Ledger<br/>events table (Append-Only)<br/>BEGIN IMMEDIATE Transactions")]
        PROJ["Deterministic Projections<br/>(Budgets, Runs, Receipts)"]
    end

    SCHED --> GATE
    GAP --> DEP
    TRANSIT --> SYNC
    PROMPT --> SVC

    GATE --> SVC
    DEP --> SVC
    SYNC --> SVC

    SVC --> POLICY
    SVC --> CREDIT
    SVC --> RETENTION
    SVC --> LEDGER
    LEDGER --> PROJ
```

## Reservation & Credit Governance Flow

```mermaid
sequenceDiagram
    autonumber
    participant S as Scheduler / Caller
    participant G as CreditGateAdapter
    participant M as AutomationMaster
    participant L as SQLite Event Ledger

    S->>G: Preflight check (work_available?)
    alt No Work Available
        G->>M: Record NO_WORK (0 credits)
        M->>L: Append DECISION_RECORDED event
        G-->>S: Allowed (Skip execution, 0 cost)
    else Work Available
        G->>M: Request Reservation (credits=N)
        M->>L: BEGIN IMMEDIATE -> Append RESERVATION_REQUESTED
        L-->>M: Reservation granted (held credits += N)
        M-->>G: Decision (ALLOWED / DENIED)
        alt Decision is ALLOWED
            G-->>S: Proceed with Job Execution
            S->>S: Run automation task
            S->>G: Report Receipt (Outcome & Metrics)
            G->>M: record_receipt(run_id, outcome, useful)
            M->>L: Append RECEIPT_RECORDED event (held -> spent)
            M->>M: Evaluate RewardPolicy & Update Projections
        else Decision is DENIED (Insufficient budget)
            G-->>S: Reject Execution (shadow mode logs only)
        end
    end
```

## Safety model

- Enforcement starts in `disabled` or `shadow` mode.
- `NO_WORK` preflight costs no credit. A late `NO_WORK` receipt releases a
  reservation.
- Hard denial applies only to ordinary comparable runs when explicitly enabled.
- Unique, safety, and deadline runs retain minimum-coverage exemptions.
- Every durable mutation is an immutable event with an event ID, node ID,
  budget epoch, entity version, optional tombstone, and content hash.
- Local reservations use `BEGIN IMMEDIATE`; cross-host state is eventually
  consistent. The module makes no global hard-atomicity claim.
- Raw payloads are not included in diagnostic exports.
- Receipt projections retain detailed fields for 30 days, then keep an audit
  summary with the immutable event metadata and payload hash; the ledger is
  never rewritten by retention.

## Quick start

```powershell
python -m pip install -e ".[dev]"
automation-master --db .\pilot.db --node workstation init
automation-master --db .\pilot.db --node workstation register-family research "Research"
automation-master --db .\pilot.db --node workstation allocate 2026-W31 research 8 seed-1
automation-master --db .\pilot.db --node workstation status --epoch 2026-W31 --scope research
```

The production default database is outside synchronized folders:
`%LOCALAPPDATA%\ellmos\automation-master\automation-master.db` on Windows or
`$XDG_STATE_HOME/ellmos/automation-master/automation-master.db` elsewhere.

## Library example

```python
from automation_master import EnforcementMode, EventStore, RunClass
from automation_master.service import AutomationMaster, CreditPolicy
from automation_master.adapters import CreditGateAdapter

master = AutomationMaster(EventStore("pilot.db"), node_id="workstation")
master.allocate_budget(
    budget_epoch="2026-W31",
    scope_id="research",
    credits=8,
    allocation_id="seed-1",
)
gate = CreditGateAdapter(
    master,
    CreditPolicy(mode=EnforcementMode.SHADOW, overdraft_limit=2),
)
decision = gate.authorize(
    run_id="run-1",
    budget_epoch="2026-W31",
    scope_id="research",
    work_item_id="paper-1",
    work_available=True,
    credits=1,
    run_class=RunClass.COMPARABLE,
)
```

## Ecosystem & Related Projects

`automation-master` is part of the **dev-bricks** ecosystem and the **open-bricks** open-source initiative:

| Project | Description | Role in Suite |
|---|---|---|
| [`DevCenter`](https://github.com/dev-bricks/DevCenter) | Developer dashboard, tool health & system orchestration | System monitoring & developer cockpit |
| [`CodeBox`](https://github.com/dev-bricks/CodeBox) | Sandboxed code execution engine & runner | Safe isolated execution runtime |
| [`MethodenAnalyser`](https://github.com/dev-bricks/MethodenAnalyser) | Test methodology & psychometrics engine | Psychological analysis & validation |
| [`companion-for-agy`](https://github.com/ellmos-ai/companion-for-agy) | PTY-based stdout-capture wrapper for agy/Gemini CLI | Multi-agent subprocess orchestration |
| [`CareCenter-for-Codex`](https://github.com/dev-bricks/CareCenter-for-Codex) | Client care documentation & clinical process assistant | Specialized assistive workflow agent |

See [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), and the
adapter contracts under `contracts/`, including
[`contracts/receipt-retention.md`](contracts/receipt-retention.md) and the
fail-closed prompt-repair verifier contract.

