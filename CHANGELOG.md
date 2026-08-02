# Changelog

## Unreleased

- Added high-resolution header banner asset and updated README documentation [G 2026-08-02].
- Align the immutable event merge adapter with the real
  `sqlite-transit-sync` Snapshot and MergeReport interfaces.
- Fail closed on foreign manifest identities, malformed semantic versions,
  and same-major downgrades in System-Gap deployment plans.
- Clarify that globally-single-writer execution still requires the
  scheduler-owned lease; a credit reservation is not a lease.

## 0.1.0 - 2026-07-28

- Added private local-first automation/family registry.
- Added append-only SQLite event ledger and deterministic projections.
- Added disabled, shadow, enforced, exemption, and bounded-overdraft decisions.
- Added explainable reward scoring with cap, decay, exploration, and hysteresis.
- Added scheduler, System-Gap, and SQLite-Transit adapter contracts.
- Added synthetic two-family/two-host pilot and failure-mode tests.
