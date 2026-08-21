# Changelog

## Unreleased

- Conducted Discoverability, README-Design, Badges, Security Parity & Ecosystem Cross-Linking Check (Pfad B) [G 2026-08-21].
- Expanded bilingual Shields.io badges in `README.md` & `README_de.md` (Pytest, Version, Python 3.10-3.13, Architecture: Event-Sourced SQLite, Platform: Windows/Linux/macOS, Privacy: Zero-Egress, Security: Local-First, License: MIT, dev-bricks, open-bricks, llms.txt).
- Added third interactive bilingual Mermaid diagram visualizing the Event Sourcing, Projection & 30-Day Receipt Retention Lifecycle in `README.md` & `README_de.md`.
- Expanded sibling ecosystem matrix across `dev-bricks`, `file-bricks`, `doc-bricks`, `ellmos-ai`, and `open-bricks` (`DevCenter`, `CodeBox`, `MethodenAnalyser`, `companion-for-agy`, `safe-start-for-codex`, `automizer-for-claude-desktop`, `CareCenter-for-Codex`, `WinStorePackager`, `ProFiler`, `ExplorerPro`, `DokuZen`, `PDFtoPDFocr`, `MediaBrain`, `ellmos-controlcenter-mcp`, `ellmos-filecommander-mcp`, `ellmos-codecommander-mcp`, `open-bricks`).
- H действия & Hardened `SECURITY.md` with complete bilingual structure (English Security Policy + Deutsch Sicherheitsrichtlinie), Local-First / Zero-Egress / User-Mode invariants, and direct contact emails (`security@ellmos.ai` and `support@lukasgeiger.com`).
- Updated `ellmos-module.v2.json` manifest with canonical repository URL (`https://github.com/dev-bricks/automation-master.git`).
- Expanded automated metadata test suite `tests/test_metadata.py` to 8 comprehensive tests covering manifest schema, required docs, API exports, llms.txt currency, SECURITY.md parity, badge parity, and Python 3.13 classifiers.
- Synchronized `llms.txt` Last-checked timestamp to `2026-08-21` with expanded API context and search phrases.

- Conducted Discoverability, README-Design, Badges & Pytest Status Check (Pfad B) [G 2026-08-16].
- Integrated interactive bilingual Mermaid system architecture and reservation sequence diagrams in `README.md` & `README_de.md`.
- Synchronized Pytest test status badges (45 passed, 100% green) across English and German documentation.
- Documented `dev-bricks` ecosystem and `open-bricks` umbrella cross-links and sibling tool references (`DevCenter`, `CodeBox`, `MethodenAnalyser`, `companion-for-agy`, `CareCenter-for-Codex`).
- Added automated repository metadata & manifest parity test suite in `tests/test_metadata.py`.
- Synchronized `llms.txt` Last-checked timestamp to `2026-08-16` with expanded API boundaries and search phrases.
- Added `pythonpath = ["src"]` to `pyproject.toml` pytest configuration, updated `llms.txt` timestamp (2026-08-03), added Shields.io badges and GFM callouts to `README.md` & `README_de.md` [G 2026-08-03].
- Added high-resolution header banner asset and updated README documentation [G 2026-08-02].
- Align the immutable event merge adapter with the real `sqlite-transit-sync` Snapshot and MergeReport interfaces.
- Fail closed on foreign manifest identities, malformed semantic versions, and same-major downgrades in System-Gap deployment plans.
- Clarify that globally-single-writer execution still requires the scheduler-owned lease; a credit reservation is not a lease.
- Add a fail-closed Antigravity-style prompt-repair contract verifier; it performs no provider mutation.
- Define a read-only 30-day detailed-receipt projection that preserves event metadata and immutable payload hashes in audit summaries.

## 0.1.0 - 2026-07-28

- Added private local-first automation/family registry.
- Added append-only SQLite event ledger and deterministic projections.
- Added disabled, shadow, enforced, exemption, and bounded-overdraft decisions.
- Added explainable reward scoring with cap, decay, exploration, and hysteresis.
- Added scheduler, System-Gap, and SQLite-Transit adapter contracts.
- Added synthetic two-family/two-host pilot and failure-mode tests.
