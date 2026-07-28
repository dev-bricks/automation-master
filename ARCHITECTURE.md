# Architecture

## Boundaries

`automation-master` owns five capabilities: automation registry, family
mapping, deterministic reward policy, epoch credit envelopes, and run
receipts. Scheduling, process execution, file distribution, and snapshot
transport stay with their respective modules.

```text
ellmos-scheduler -> CreditGateAdapter -> AutomationMaster -> local SQLite events
system-gap-master -> DeploymentPlan validator ------^
sqlite-transit-sync -> immutable merge policy ------^
```

## Event model

The `events` table is append-only. Projection order never depends on wall-clock
time. Set-like projections use event identity; versioned registry projections
use `(event_version, event_id)`. A duplicate event or dedupe key must have the
same semantic content, otherwise merge fails closed.

Budget state is derived per `(budget_epoch, scope_id)`:

```text
available = allocations + handovers_in - handovers_out - held - spent
```

Epochs never borrow from each other. Handovers are paired immutable in/out
events. Returns are reverse handovers with their own stable transfer identity.

## Reservation protocol

1. Scheduler performs a free work-item preflight.
2. `NO_WORK` records a decision without a reservation.
3. An eligible run requests a local reservation in a SQLite
   `BEGIN IMMEDIATE` transaction.
4. A final receipt consumes or releases the reservation.
5. Repeated run IDs and receipt IDs are idempotent.

This prevents double allocation inside a single local database. Offline hosts
can continue within their previously synchronized envelopes. After
reconnection, immutable events converge; separate per-host envelopes prevent
two hosts from spending the same assigned credits.

## Reward policy

Positive signals: current interest, uncovered gap, deadline pressure, useful
output, and independent-review value.

Negative signals: cost per useful result, `NO_WORK` rate, error rate, and
redundancy.

The calculation is deterministic and exposes every weighted component. Caps,
decay, hysteresis, bounded per-epoch movement, and an exploration floor prevent
runaway reinforcement. Default weights are provisional implementation defaults
and must be replaced by a versioned policy after shadow observation.

Receipt projections provide useful-result, `NO_WORK`, and error rates. They
produce versioned throttle proposals, never direct scheduler mutations.
Versioned human overrides require an actor and reason and remain in the audit
ledger. Overdraft events expose bounded warning records for an optional `.SYNC`
exporter; the core does not write directly into another module's slot.

## Integration guarantees

- Scheduler adapter: authorization only; no timers or process launch.
- System-Gap adapter: plan/diff validation, health check, and rollback plan;
  no foreign-slot write.
- SQLite-Transit adapter: immutable union, conflict detection, no updates.
- Core runtime has no network dependency.

## Future Automation Health adapter

Provider prompt repair is a future, separate adapter capability rather than a
core-ledger responsibility. It may repair a known provider prompt only when a
provider-specific parser and validator can prove a minimal prompt-only change.
The transaction must create a backup, preserve model, thinking level, schedule,
enabled/status state, target, and working directory, validate and read back the
provider configuration, roll back on any mismatch, and emit a receipt whose
diff contains no secret values. Antigravity-style prompt self-healing can use
the same contract through its own provider adapter.

No generic TOML/text rewrite is safe enough for this path. Unknown providers or
unverifiable fields remain manual. This 0.1.0 implementation documents the seam
but does not mutate provider automation configuration.
