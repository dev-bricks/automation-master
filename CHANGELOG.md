# Changelog

## Unreleased

- Conducted Discoverability, README-Design, Badges & Pytest Status Check (Pfad B) [G 2026-08-16].
- Integrated interactive bilingual Mermaid system architecture and reservation sequence diagrams in `README.md` & `README_de.md`.
- Synchronized Pytest test status badges (45 passed, 100% green) across English and German documentation.
- Documented `dev-bricks` ecosystem and `open-bricks` umbrella cross-links and sibling tool references (`DevCenter`, `CodeBox`, `MethodenAnalyser`, `companion-for-agy`, `CareCenter-for-Codex`).
- Added automated repository metadata & manifest parity test suite in `tests/test_metadata.py`.
- Synchronized `llms.txt` Last-checked timestamp to `2026-08-16` with expanded API boundaries and search phrases.
- Added `pythonpath = ["src"]` to `pyproject.toml` pytest configuration, updated `llms.txt` timestamp (2026-08-03), added Shields.io badges and GFM callouts to `README.md` & `README_de.md` [G 2026-08-03].
- Added high-resolution header banner asset and updated README documentation [G 2026-08-02].
- Align the immutable event merge adapter with the real
  `sqlite-transit-sync` Snapshot and MergeReport interfaces.
- Fail closed on foreign manifest identities, malformed semantic versions,
  and same-major downgrades in System-Gap deployment plans.
- Clarify that globally-single-writer execution still requires the
  scheduler-owned lease; a credit reservation is not a lease.
- Add a fail-closed Antigravity-style prompt-repair contract verifier; it
  performs no provider mutation.
- Define a read-only 30-day detailed-receipt projection that preserves event
  metadata and immutable payload hashes in audit summaries.

## 0.1.0 - 2026-07-28

- Added private local-first automation/family registry.
- Added append-only SQLite event ledger and deterministic projections.
- Added disabled, shadow, enforced, exemption, and bounded-overdraft decisions.
- Added explainable reward scoring with cap, decay, exploration, and hysteresis.
- Added scheduler, System-Gap, and SQLite-Transit adapter contracts.
- Added synthetic two-family/two-host pilot and failure-mode tests.
