# Automation Runtime Observation Contract

## Purpose

`AutomationRuntime` is the logical provider for `module:automation-runtime`. It
records bounded evidence about an automation run after provider-native and
scheduler-native readback. It is an observer and receipt store, not an
automation definition authority, scheduler, process launcher, or policy engine.

## Required evidence

Every runtime receipt must contain:

- a portable receipt ID and automation definition version;
- an execution class and immutable execution pin for non-app-native runs;
- timezone-aware schedule, start, and finish timestamps;
- provider-native and scheduler-native readback metadata;
- exactly one resolved authority input for rules, policies, decisions,
  workflows, and approved user preferences;
- SHA-256-only input fingerprints;
- a bounded, redacted output summary;
- a mutation class and optional stable rollback reference.

Receipts use the closed schema `ellmos.automation-runtime-receipt.v1`. Unknown
fields, missing authority inputs, raw prompts, personal payloads, credential-like
values, mutable execution references, and cloud-synchronized receipt roots fail
closed.

## Native readback adapters

`read_provider_receipt` reads a bounded UTF-8 JSON receipt and returns only the
selected native receipt ID, status, observation time, source identity, and a
SHA-256 digest of the exact bytes. It never exports the source path or raw
provider payload.

`read_scheduler_run` opens an `ellmos-scheduler` SQLite database through a
read-only immutable handle. It accepts only the expected `runs` columns, refuses
a non-empty live WAL, and projects only run identity, scheduling metadata,
status, and authority fingerprint into a content hash. It never returns output,
error, payload, or filesystem path fields.

Provider-specific selectors may be configured explicitly at the CLI boundary;
unknown layouts fail closed.

## Storage and statistics

`RuntimeReceiptStore` writes one create-only JSON file per receipt outside
configured OneDrive roots. Repeating identical content is idempotent. Reusing a
receipt ID with different content raises a conflict. Reads verify the stored
content hash before returning data.

`AutomationRuntime.statistics()` exposes only receipt count, counts by status,
and the latest finish time. It does not expose automation IDs, input details, or
output summaries.

## Ownership boundary

- Automation definitions and approval state remain with their owning registry.
- Due time, leases, dispatch, and retry decisions remain with the scheduler.
- Rules, policies, decisions, workflows, and user preferences remain with their
  respective authorities.
- Provider execution remains with the provider.
- `AutomationRuntime` only validates, stores, and summarizes post-run evidence.

No contract in this module authorizes activation, provider mutation,
publication, or hard enforcement.
