# Changelog

## [Unreleased]

- **Pfad B Discoverability, Level 1 SBOM Re-Audit & Design Currency (2026-10-09)**:
  - Re-audited Level 1 SBOM plain-text companion `THIRD_PARTY_LICENSES.txt` and `THIRD_PARTY_LICENSES.md` to Stand 2026-10-09, verifying 100% pure Python standard library runtime purity (`dependencies = []`), zero copyleft, and unprivileged RunAsInvoker execution (`INV-PRIV-02`).
  - Recorded live traffic baseline via GitHub API (36 clones / 1 unique in 14 days, 0 views).
  - Synchronized Shields.io verification and statutory badges across `README.md` and `README_de.md` (`Verified: 2026-10-09` / `Geprüft: 2026-10-09`, `Statutory Notice: § 521 BGB` / `Gesetzlicher Hinweis: § 521 BGB`, `Pytest: 107 passed | 100%`) while preserving all 18 bilateral reciprocal HTML anchors (`<a id="sec-01"></a>` through `<a id="sec-18"></a>`) and ASCII Four-View Topology projections.
  - Updated `llms.txt` context index (Stand: 2026-10-09, 107+ verified tests baseline).
  - Recorded Section 9 in `MARKETING-LOG.txt` (Pfad B Re-Audit Stand: 2026-10-09) with live traffic telemetry and 3 actionable discoverability & design recommendations (`REC-MKT-20261009-01..03`).
  - Expanded automated contract test suite in `tests/test_metadata.py` with `test_pfad_b_discoverability_audit_recency_20261009` (107 passed tests).
  - Strictly preserved frozen release version `0.1.6` pursuant to governance invariant `T-20260920-167562623`.

- **Pfad B Discoverability, Level 1 SBOM Re-Audit & Design Currency (2026-10-03)**:
  - Re-audited Level 1 SBOM plain-text companion `THIRD_PARTY_LICENSES.txt` and `THIRD_PARTY_LICENSES.md` to Stand 2026-10-03, verifying 100% pure Python standard library runtime purity (`dependencies = []`), zero copyleft, and unprivileged RunAsInvoker execution (`INV-PRIV-02`).
  - Synchronized Shields.io verification badges across `README.md` and `README_de.md` (`Verified: 2026-10-03` / `Geprüft: 2026-10-03`, `Pytest: 105 passed | 100%`) while preserving all 18 bilateral reciprocal HTML anchors (`<a id="sec-01"></a>` through `<a id="sec-18"></a>`) and ASCII Four-View Topology projections.
  - Updated `llms.txt` context index (Stand: 2026-10-03, 105 verified tests baseline).
  - Recorded Section 8 in `MARKETING-LOG.txt` (Pfad B Re-Audit Stand: 2026-10-03) with non-automated marketing & design recommendations for high-DPI social preview cards, interactive terminal workflow animations, and sibling integration guides.
  - Expanded automated contract test suite in `tests/test_metadata.py` with `test_pfad_b_discoverability_audit_recency_20261003` (106+ passed tests).
  - Strictly preserved frozen release version `0.1.6` pursuant to governance invariant `T-20260920-167562623`.

- **Pfad A Repository-Hygiene, CI Lifecycle Workflows, Multi-Host Lock-Schutz & Vertragstest-Erweiterung (2026-10-01)**:
  - Deployed `.github/workflows/auto-assign.yml` with `actions/github-script@v7` (5-minute timeout, concurrency `cancel-in-progress: true`, least-privilege `pull-requests: write`, `issues: write`) for unprivileged PR assignment.
  - Deployed `.github/workflows/label-sync.yml` with `EndBug/label-sync@v2` (5-minute timeout, concurrency `cancel-in-progress: true`, least-privilege `issues: write`) and canonical `.github/labels.yml` with 11 standard governance labels according to GOVERNANCE.md §4.2.
  - Created bilingual `CONTRIBUTING.md` (DE/EN) establishing governance invariants `INV-LOCAL-01` through `INV-ISOLAT-10`, unprivileged RunAsInvoker execution (`INV-PRIV-02`), Plan D clone workflow, and pre-commit quality gates.
  - Hardened `.gitignore` against multi-host conflict tokens (`*-IDEAPAD*`, `*-IDEAPAD-GEI*`, `*_WORKSTATION*`, `*_WORKSTATION-LG*`), canonical locks (`LOCK.dev.*`, `LOCK.antigravity.*`, `LOCK.bugsearch.*`), OS/editor metadata (`*.swo`, `Desktop.ini`, `ehthumbs.db`), and task tracking patterns (`TASKPLAN_*.md`).
  - Standardized PEP 621 `pyproject.toml` by registering `Contributing` URL under `[project.urls]`, setting `addopts = "-ra -v --basetemp=.pytest_temp"`, and expanding `norecursedirs` with `.pytest_temp`, `.pytest_tmp*`, `.hypothesis`, `.turbo`, `.nyc_output`, and `.tox`.
  - Re-audited Level 1 SBOM in `THIRD_PARTY_LICENSES.md` and plain-text companion `THIRD_PARTY_LICENSES.txt` (Stand 2026-10-01) confirming pure Python standard library runtime purity (`dependencies = []`), zero copyleft, and unprivileged RunAsInvoker execution.
  - Synchronized verification badges across `README.md` and `README_de.md` (`Verified: 2026-10-01` / `Geprüft: 2026-10-01`, `Contributing: Welcome` / `Mitwirken: Willkommen`) while strictly preserving all 18 bilateral reciprocal HTML anchors (`<a id="sec-01"></a>` through `<a id="sec-18"></a>`).
  - Updated `llms.txt` context index (Stand 2026-10-01) and recorded Section 7 in `MARKETING-LOG.txt`.
  - Expanded automated contract test suite in `tests/test_metadata.py` with 6 new contract tests for CI lifecycle workflows, governance labels, contributing documentation, ignore patterns, and SBOM audit recency.
  - Strictly preserved frozen version `0.1.6` pursuant to governance invariant `T-20260920-167562623`.

- **Pfad B Discoverability, 18-Point Dual Anchors & Level 1 SBOM Text Companion (2026-09-28)**:
  - Upgraded `README.md` and `README_de.md` quick navigation to standardized 18-point dual reciprocal HTML anchors (`<a id="sec-01"></a>` through `<a id="sec-18"></a>`) with explicit operational scope descriptions.
  - Added ASCII Four-View Architectural Topology projection in Section 2 across both English and German documentation, mapping View 1 (Client Runtimes & Agent Drivers), View 2 (Core Governance Engine), View 3 (Atomic SQLite Persistence & Concurrency), and View 4 (Governance, Security & Perimeter).
  - Created root plain-text Level 1 SBOM companion file `THIRD_PARTY_LICENSES.txt` with complete inventory, zero-copyleft certification, RunAsInvoker non-elevation attestation, and Invariant Cross-Reference Matrix table (INV-LOCAL-01..INV-ISOLAT-10 all verified).
  - Saturated `pyproject.toml` keywords to exactly 20/20 items and added `Third-Party Licenses (Text)`, `Level 1 SBOM`, and `Plain-Text Licenses` companion URLs in `[project.urls]`.
  - Registered `THIRD_PARTY_LICENSES.txt` in `pyproject.toml` `license-files` whitelist and synchronized `THIRD_PARTY_LICENSES.md` audit recency (Stand 2026-09-28).
  - Synchronized Shields.io badges across `README.md` and `README_de.md` (`Level 1 SBOM: Text Companion`, `Verified: 2026-09-28` / `Geprüft: 2026-09-28`).
  - Updated `llms.txt` context index with 2026-09-28 recency, verified test suite baseline, and plain-text companion links.
  - Expanded contract test suite in `tests/test_metadata.py` verifying reciprocal dual anchors, ASCII topology projection, 20 saturated keywords, and SBOM companion integrity.
- **CI Workflow Provisioning & Hardening**: Deployed `.github/workflows/welcome.yml` with `actions/first-interaction@v3` (5-minute timeout, concurrency `cancel-in-progress: true`, least-privilege `issues: write`, `pull-requests: write`) and `.github/workflows/stale.yml` with `actions/stale@v9` (10-minute timeout, concurrency `cancel-in-progress: true`, least-privilege permissions); hardened `.github/workflows/ci.yml` with least-privilege `permissions: contents: read`.
- **Multi-Host Conflict, Lock & Cache Defense**: Expanded `.gitignore` with multi-host conflict patterns (`*-ASUS*`, `*-LAPTOP*`, `*-Mac Studio*`, `*-MacBook*`), canonical lock patterns (`LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`, `.automation-lock`), package manager preservation (`!package-lock.json`), and test/build cache directories (`.pytest_temp/`, `.pytest_tmp*/`, `.hypothesis/`, `.turbo/`, `.nyc_output/`, `.tox/`, `*.orig`, `*.rej`).
- **PEP 621 Metadata & Pytest Standardization**: Standardized `pyproject.toml` by configuring `Notice` URL in `[project.urls]` pointing to canonical root `NOTICE`, added `minversion = "7.0"` and `norecursedirs = [".git", ".pytest_cache", "__pycache__", "build", "dist", ".venv"]` to `[tool.pytest.ini_options]`; strictly preserved frozen release version per rule `T-20260920-167562623`.
- **Level 1 SBOM & Third-Party License Re-Audit**: Re-audited `THIRD_PARTY_LICENSES.md` (Stand 2026-09-24) confirming pure Python standard library runtime (`dependencies = []`), RunAsInvoker non-elevation certification, and zero-copyleft permissive licensing.
- **Synchronized Context & Discoverability**: Updated `llms.txt` Last-checked timestamp to 2026-09-24 and recorded verification baseline; updated `TODO.md` with completed Pfad A hygiene tasks.
- **Contract Test Suite Expansion**: Expanded `tests/test_metadata.py` with automated contract tests verifying CI workflows (`welcome.yml`, `stale.yml`, `ci.yml` permissions), `.gitignore` multi-host and lock defenses, `pyproject.toml` Notice URL and pytest settings, and audit date recency.

## [0.1.6] - 2026-09-21

- Added version-bound, immutable `AUTOMATION_DEFINITION_BOUND` declarations with explicit source, owner, provider, execution class and conditional execution pin. The content-free projection keeps declaration completeness separate from provider-native and runtime state.
- Fixed import-aware definition-binding conflict handling and PEP 621 license metadata for current editable builds.

## [0.1.5] - 2026-09-20

- **Bilingual 18-Point Quick Navigation & Dual Reciprocal HTML Anchors**: Upgraded quick navigation across `README.md` and `README_de.md` to 18 points with full bidirectional reciprocal anchor parity and dual HTML anchors (`<a id="..."></a>`), ensuring clean linking across both English and German documentation.
- **Explicit Target Personas (`[PERSONA-01]` to `[PERSONA-04]`)**: Formally structured the target personas section with identifiers `[PERSONA-01]` (Autonomous AI Agent Engineers & Swarm Operators), `[PERSONA-02]` (DevOps & Automation Architects), `[PERSONA-03]` (Edge & Air-Gapped Systems Developers), and `[PERSONA-04]` (Enterprise Security & Compliance Officers), accompanied by bilingual search intent matrices.
- **10-Dimension 5-Way Comparative Matrix**: Added comprehensive comparative matrix evaluating `automation-master` across 10 architectural dimensions (`INV-LOCAL-01` to `INV-ISOLAT-10`) against 4 standard alternatives (cron/systemd, Airflow/Prefect, AWS Budgets, and ad-hoc scripts).
- **Statutory Notice & Liability Limitation (§ 521 BGB)**: Added Section 18 to both READMEs establishing formal German statutory liability limitation under § 521 BGB (*Gefälligkeitsrecht / unentgeltliche Zuwendung*) restricting liability to intentional misconduct and gross negligence.
- **Canonical Root `NOTICE` File & PEP 639 Synchronization**: Created root `NOTICE` file attributing Lukas Geiger and the dev-bricks/open-bricks ecosystems, synchronized PEP 639 `license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md"]` in `pyproject.toml`, and integrated attribution badges.
- **Level 1 SBOM & Invariant Cross-Reference Matrix**: Upgraded `THIRD_PARTY_LICENSES.md` with a complete Level 1 Software Bill of Materials (SBOM), Invariant Cross-Reference Matrix table, RunAsInvoker non-elevation certification, and zero-copyleft permissive licensing guarantee.
- **Remote GitHub Discoverability Metadata**: Updated remote GitHub repository metadata with 20 high-relevance topics and homepage URL pointing directly to `#readme`.
- **Contract Test Suite Expansion**: Expanded automated test suite in `tests/test_metadata.py` with contract tests verifying 18-point quick navigation reciprocal anchors, personas, comparative matrix, NOTICE attribution, § 521 BGB disclaimer, Level 1 SBOM, and semicolon-free Mermaid diagrams.
- **Version & Manifest Parity**: Bumped version to `0.1.5` across `pyproject.toml`, `src/automation_master/__init__.py`, `ellmos-module.v2.json`, `README.md`, `README_de.md`, `MARKETING-LOG.txt`, and `llms.txt`.

## [0.1.4] - 2026-09-13

- **PEP 561 Typing Marker**: Added `src/automation_master/py.typed` marker and packaged it via `tool.setuptools.package-data` in `pyproject.toml` to guarantee first-class static type-checking integration for consumers (Mypy, Pyright).
- **Executable Module & CLI Entrypoint Hardening**: Added `src/automation_master/__main__.py` enabling direct module invocation via `python -m automation_master` as specified in `ellmos-module.v2.json`, added explicit `--version` / `-v` flag handling to `automation_master.cli`, and ensured clean execution return semantics.
- **CI Matrix Timeout Guardrail**: Hardened `.github/workflows/ci.yml` with a 15-minute job timeout guardrail (`timeout-minutes: 15`) across all matrix targets (`ubuntu-latest`, `windows-latest`, `macos-latest` on Python 3.10-3.13) to prevent hung runner tasks.
- **Gitignore Hardening**: Expanded `.gitignore` with type checker cache directories (`.mypy_cache/`, `.dmypy.json`, `dmypy.json`, `.pyre/`, `.pytype/`) and coverage wildcards (`.coverage.*`).
- **Contract Test Suite Expansion**: Added 3 new automated contract tests in `tests/test_metadata.py` verifying PEP 561 typing markers, CLI version & module entrypoint integrity, and CI workflow timeout guardrails (74/74 passed | 100% green).
- **Metadata Parity & Version Synchronization**: Bumped version to `0.1.4` across `pyproject.toml`, `src/automation_master/__init__.py`, `ellmos-module.v2.json`, `README.md`, `README_de.md`, `TODO.md`, and `llms.txt`; synchronized test count badge (74 passed | 100% green) and Last-checked timestamp (2026-09-13).

## [0.1.3] - 2026-09-12

- **Bilingual 16-Point Quick Navigation & Visual Architecture**: Upgraded quick navigation across `README.md` and `README_de.md` to 16 points with 100% reciprocal markdown anchor parity, introducing dedicated sections for Target Personas & Discoverability (`#target-personas--discoverability` / `#zielgruppen--auffindbarkeit`) and Third-Party Licenses & Transparency (`#third-party-licenses--transparency` / `#drittanbieter-lizenzen--transparenz`).
- **Target Personas & Market Positioning**: Established formal personas targeting Autonomous AI Agent Engineers, DevOps & Automation Architects, Edge/Air-Gapped Systems Developers, and Enterprise Security & Compliance Officers with bilingual high-intent discovery query matrices.
- **PEP 621 Extended Project URLs**: Enriched `pyproject.toml` `[project.urls]` table with canonical links to `Third-Party Licenses`, `Marketing-Log`, and `LLM-Ready` resources.
- **Comprehensive Third-Party License Audit**: Updated `THIRD_PARTY_LICENSES.md` audit confirming zero external runtime dependencies (`dependencies = []`), standard library runtime purity, and mapping directly to the 10 Governance Invariants (`INV-LOCAL-01` to `INV-ISOLAT-10`).
- **Enriched Marketing & Discoverability Log**: Expanded `MARKETING-LOG.txt` with structured operational audit trails, 4 persona journeys, bilingual keyword matrices, 5-way competitive matrix across 10 architectural dimensions, and 21 sibling ecosystem partner tools.
- **Canonical Governance Invariant IDs**: Integrated standardized identifiers (`INV-LOCAL-01` through `INV-ISOLAT-10`) into README invariant tables, `llms.txt`, and license documentation.
- **Metadata Contract Test Suite Expansion**: Added 5 new automated contract tests in `tests/test_metadata.py` verifying 16-point quick navigation reciprocal parity, extended PEP 621 URLs, target personas presence, competitive matrix integrity, and canonical invariant IDs (71/71 passed | 100% green).

## [0.1.2] - 2026-09-10

- **Technical Hygiene & Path A Hardening**: Comprehensive maintenance pass across repository metadata, testing configurations, and ignore rules.
- **Gitignore Hardening**: Expanded `.gitignore` with multi-host synchronization conflict patterns (`*.sync-temp-*`, `*-ASUS-GEI.*`, `*-WORKSTATION-LG.*`, `*-WORKSTATION.*`), multi-agent locks (`LOCK`, `LOCK.permissions.json`, `uv.lock`), coverage/packaging scratch directories (`coverage/`, `wheelhouse/`, `.wheel-smoke/`), and temporary editor/log files (`*.tmp`, `*.bak`, `*.swp`, `*~`, `*.log`).
- **Standardized Pytest & CI Configuration**: Standardized `pyproject.toml` pytest options (`addopts = "-ra -v"`) and updated `.github/workflows/ci.yml` test step to execute `pytest -ra -v`.
- **Contract Test Suite Expansion**: Added automated contract tests in `tests/test_metadata.py` verifying gitignore hygiene patterns, pytest flag configuration, CI workflow flags, changelog currency, PEP 639 license inventory, TODO status table format, and Gate 1-10 compliance (66 passed | 100% green).
- **Final Gate Check & PEP 639 Compliance**: Reached full compliance across all 10 release gates (`final_gate_check.py`), added `THIRD_PARTY_LICENSES.md` certifying zero external runtime dependencies, and configured `license-files` in `pyproject.toml`.
- **Documentation & Badge Synchronization**: Bumped version to `0.1.2` across `pyproject.toml`, `src/automation_master/__init__.py`, `ellmos-module.v2.json`, `README.md`, `README_de.md`, and `llms.txt`; synchronized test count badge (66 passed | 100% green) and Last-checked timestamp (2026-09-10).

## [0.1.1] - 2026-09-09

- **Bilingual 14-Point Quick Navigation**: Added full 14-point quick navigation (`Quick Navigation` / `Schnellnavigation`) with explicit markdown anchor parity across `README.md` and `README_de.md`.
- **10 Governance & Runtime Invariants Table**: Integrated standardized high-contrast table of ten verifiable architectural guarantees (Zero-Egress, Non-Elevation, Append-Only Event Ledger, Atomic Reservations, Fail-Closed Credit Gating, Zero Cost for NO_WORK, Critical Exemptions, 30-Day Retention, Multi-OS Parity, Cloud-Sync Isolation) in both English and German documentation.
- **CI Hardening**: Enhanced `.github/workflows/ci.yml` with workflow-level concurrency (`cancel-in-progress: true`) and pre-test bytecode verification (`python -m compileall -q src tests`).
- **Synchronized Badges & SLAs**: Added Ruff Code Style badge, 48h Security SLA badge, Parent Organization URL, and updated Pytest test badge (59 passed | 100% green); hardened `SECURITY.md` with explicit 48-Hour Response SLA and 5-Day Triage commitment.
- **Ecosystem Matrix Expansion**: Expanded sibling tools matrix to 21 repositories across `dev-bricks`, `ellmos-ai`, `file-bricks`, `doc-bricks`, and `open-bricks`.
- **Repository Hygiene & Gitignore Hardening**: Added synchronization conflict ignore patterns (`*.sync-conflict-*`, `*.conflict`, `*-CONFLIT-*`, `*-conflict-*`) and multi-agent lock patterns (`LOCK.*`, `*.lock`, `LOCK*.txt`) to `.gitignore`.
- **Metadata Contract Test Suite**: Expanded `tests/test_metadata.py` with 8 new automated parity and contract verification tests (59/59 passed).

## [0.1.1] - 2026-08-23


- **GitHub Actions Multi-OS CI Workflow**: Added `.github/workflows/ci.yml` supporting Multi-OS matrix (`ubuntu-latest`, `windows-latest`, `macos-latest`) and Python versions `['3.10', '3.11', '3.12', '3.13']` with Pip caching, ruff linting gate, and pytest test suite.
- **PEP 621 Standard Classifiers & Metadata**: Expanded `pyproject.toml` with PEP 621 Classifiers (`Development Status :: 4 - Beta`, `OS Independent`, `POSIX Linux`, `Microsoft Windows`, `MacOS`, `Topic Software Development Build Tools`, `Topic System Administration`), keywords, dev dependencies, and full `[project.urls]` table (`Homepage`, `Documentation`, `Repository`, `Issues`, `Changelog`, `Security`, `Umbrella`).
- **Bilingual Security Policy Hardening**: Hardened `SECURITY.md` with umbrella contact `lukas@open-bricks.org` alongside `security@ellmos.ai` and `support@lukasgeiger.com`, direct GitHub Security Advisories reporting link, and Supported Versions matrix table.
- **Expanded Contract & Invariant Tests**: Expanded `tests/test_metadata.py` with `test_ci_workflow_integrity`, `test_pyproject_pep621_classifiers_and_urls`, and `test_offline_and_privacy_invariants` (11 contract tests, 51/51 passed).
- **Version & Manifest Parity**: Bumped version to `0.1.1` across `pyproject.toml`, `src/automation_master/__init__.py`, `ellmos-module.v2.json`, and `llms.txt`.
- **Badges & Documentation Sync**: Updated `README.md` and `README_de.md` with CI workflow badge, 51 passed tests badge, and version 0.1.1 badge; synchronized `llms.txt` Last-checked timestamp to `2026-08-23`.

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
