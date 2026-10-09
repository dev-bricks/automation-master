from __future__ import annotations

import json
from pathlib import Path

import automation_master

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_version_parity():
    """Verify version parity across pyproject.toml, package, manifest, and changelog."""
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{automation_master.__version__}"' in pyproject_text

    manifest = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert manifest["version"] == automation_master.__version__

    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    ver_tag = automation_master.__version__
    assert f"## [{ver_tag}]" in changelog_text or f"## {ver_tag}" in changelog_text


def test_manifest_structure_and_schema():
    """Validate ellmos-module.v2.json structure and capabilities."""
    manifest = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert manifest["schema"] == "ellmos.module.v2"
    assert manifest["id"] == "automation-master"
    assert manifest["category"] == "control"
    assert "automation.registry" in manifest["provides"]
    assert "automation.budget" in manifest["provides"]
    assert "automation.credit" in manifest["provides"]
    assert len(manifest["adapters"]) >= 3
    assert manifest["source_of_truth"]["repository"] == "https://github.com/dev-bricks/automation-master.git"


def test_required_docs_exist_and_non_empty():
    """Ensure all core architectural and discoverability documentation exists."""
    required = [
        "README.md",
        "README_de.md",
        "llms.txt",
        "CHANGELOG.md",
        "ARCHITECTURE.md",
        "SECURITY.md",
        "LICENSE",
        "NOTICE",
        "THIRD_PARTY_LICENSES.md",
        "ellmos-module.v2.json",
    ]
    for filename in required:
        file_path = REPO_ROOT / filename
        assert file_path.is_file(), f"Missing required file: {filename}"
        assert file_path.stat().st_size > 0, f"File is empty: {filename}"


def test_public_api_exports():
    """Ensure public API symbols are properly exported."""
    expected_symbols = [
        "AutomationMaster",
        "AutomationSpec",
        "BudgetState",
        "CreditPolicy",
        "EnforcementMode",
        "EventStore",
        "RewardPolicy",
        "RewardResult",
        "RewardSignals",
        "ReceiptRetentionClass",
        "ReceiptRetentionPolicy",
        "project_receipt",
        "project_receipts",
        "AntigravityPromptRepairContractAdapter",
    ]
    for symbol in expected_symbols:
        assert hasattr(automation_master, symbol), f"Missing exported symbol: {symbol}"
        assert symbol in automation_master.__all__, f"{symbol} not in __all__"


def test_llms_txt_integrity():
    """Validate llms.txt context file content and markers."""
    llms_text = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "# automation-master" in llms_text
    assert "AutomationMaster" in llms_text
    assert "RewardPolicy" in llms_text
    assert "Last-checked: 2026-10-01" in llms_text
    assert "0.1.6" in llms_text

    assert "INV-LOCAL-01" in llms_text
    assert "NOTICE" in llms_text
    assert "CONTRIBUTING.md" in llms_text
    assert "THIRD_PARTY_LICENSES.txt" in llms_text
    assert "MARKETING-LOG.txt" in llms_text


def test_security_policy_bilingual_and_contacts():
    """Verify that SECURITY.md contains bilingual sections, valid contacts, and invariants."""
    sec_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "English: Security & Trust Model" in sec_text
    assert "Deutsch: Sicherheitsrichtlinie" in sec_text
    assert "security@ellmos.ai" in sec_text
    assert "support@lukasgeiger.com" in sec_text
    assert "lukas@open-bricks.org" in sec_text
    assert "github.com/dev-bricks/automation-master/security/advisories" in sec_text
    assert "Supported Versions" in sec_text
    assert "Zero-Egress" in sec_text or "Null Netzwerk-Egress" in sec_text
    assert "BEGIN IMMEDIATE" in sec_text


def test_readme_bilingual_badges_and_mermaid():
    """Verify that both README.md and README_de.md contain badges and Mermaid diagrams."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for readme in (readme_en, readme_de):
        assert "shields.io" in readme
        assert "```mermaid" in readme
        assert "sequenceDiagram" in readme
        assert "dev-bricks" in readme
        assert "open-bricks" in readme
        assert "DevCenter" in readme
        assert "CodeBox" in readme
        assert "companion-for-agy" in readme
        assert "security@ellmos.ai" in readme


def test_pyproject_pep621_classifiers_and_urls():
    """Verify PEP 621 classifiers, keywords, settings, and project.urls."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'Development Status :: 4 - Beta' in pyproject
    assert 'Programming Language :: Python :: 3.10' in pyproject
    assert 'Programming Language :: Python :: 3.11' in pyproject
    assert 'Programming Language :: Python :: 3.12' in pyproject
    assert 'Programming Language :: Python :: 3.13' in pyproject
    assert 'Operating System :: OS Independent' in pyproject
    assert 'Operating System :: Microsoft :: Windows' in pyproject
    assert 'Operating System :: POSIX :: Linux' in pyproject
    assert 'Operating System :: MacOS' in pyproject
    assert 'Topic :: Software Development :: Build Tools' in pyproject
    assert 'Topic :: System :: Systems Administration' in pyproject
    assert 'pytest' in pyproject
    assert 'ruff' in pyproject

    assert '[project.urls]' in pyproject
    assert 'Homepage = "https://github.com/dev-bricks/automation-master"' in pyproject
    assert 'Documentation = "https://github.com/dev-bricks/automation-master#readme"' in pyproject
    assert 'Repository = "https://github.com/dev-bricks/automation-master.git"' in pyproject
    assert 'Issues = "https://github.com/dev-bricks/automation-master/issues"' in pyproject
    assert 'CHANGELOG.md' in pyproject
    assert 'SECURITY.md' in pyproject
    assert 'Umbrella = "https://github.com/open-bricks"' in pyproject
    assert '"Parent Organization" = "https://github.com/dev-bricks"' in pyproject



def test_ci_workflow_integrity():
    """Ensure GitHub Actions CI workflow exists and tests multi-OS with Python 3.10-3.13."""
    ci_file = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_file.is_file(), "CI workflow file .github/workflows/ci.yml must exist"
    ci_text = ci_file.read_text(encoding="utf-8")

    assert "ubuntu-latest" in ci_text
    assert "windows-latest" in ci_text
    assert "macos-latest" in ci_text
    assert '"3.10"' in ci_text
    assert '"3.11"' in ci_text
    assert '"3.12"' in ci_text
    assert '"3.13"' in ci_text
    assert "actions/checkout@v4" in ci_text
    assert "actions/setup-python@v5" in ci_text
    assert "ruff check ." in ci_text
    assert "pytest" in ci_text
    assert "permissions:" in ci_text
    assert "contents: read" in ci_text


def test_offline_and_privacy_invariants():
    """Verify local-first, zero-egress, and non-elevation guarantees."""
    manifest = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert manifest["boundaries"]["network"] == "none"
    assert "windows" in manifest["boundaries"]["platforms"]
    assert "linux" in manifest["boundaries"]["platforms"]
    assert "macos" in manifest["boundaries"]["platforms"]

    sec_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "Zero-Egress" in sec_text
    assert "Non-Elevation" in sec_text or "User-Mode" in sec_text
    assert "No Credential Logging" in sec_text


def test_readme_de_exists_and_bilingual_parity():
    """Verify README_de.md exists and maintains structural parity with README.md."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert len(readme_en) > 1000
    assert len(readme_de) > 1000
    assert "shields.io" in readme_de
    assert "Architektur" in readme_de
    assert "sequenceDiagram" in readme_de


def test_quick_navigation_anchors_and_parity():
    """Verify 18-point quick navigation exists in both README.md and README_de.md."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "### Quick Navigation" in readme_en
    assert "### Schnellnavigation" in readme_de

    en_points = [
        "1. Executive Summary & Core Identity",
        "2. Visual Architecture & System Topology",
        "3. End-to-End Governance & Credit Lifecycle",
        "4. Target Personas & High-Intent SEO Queries",
        "5. Comparative Matrix vs. Alternatives",
        "6. Governance & Runtime Invariants Matrix",
        "7. Event Sourcing & Projection Lifecycle",
        "8. Installation & Prerequisites",
        "9. CLI Usage & Operations",
        "10. Python API Integration & Extension Points",
        "11. Data Storage & Multi-OS Layout",
        "12. Architectural Contracts & Schema Specifications",
        "13. Sibling Tools & Ecosystem Matrix",
        "14. Testing, Verification & Quality Gates",
        "15. Security Policy & Vulnerability SLAs (48h Response SLA)",
        "16. Third-Party Licenses & Level 1 SBOM",
        "17. Discovery Keywords & AI Agent Index",
        "18. Statutory Notice, Liability Limitation & License (§ 521 BGB)",
    ]
    for pt in en_points:
        assert pt in readme_en, f"Missing English quick navigation point: {pt}"

    de_points = [
        "1. Übersicht & Management Summary",
        "2. Visuelle Systemarchitektur & Topologie",
        "3. End-to-End Governance- & Credit-Lebenszyklus",
        "4. Zielgruppen & High-Intent Suchbegriffe",
        "5. Vergleichsmatrix gegenüber Alternativen",
        "6. Governance- & Laufzeit-Invarianten-Matrix",
        "7. Event-Sourcing- & Projektionslebenszyklus",
        "8. Installation & Voraussetzungen",
        "9. CLI-Bedienung & Betrieb",
        "10. Python-API-Integration & Erweiterungspunkte",
        "11. Datenspeicher & Multi-OS-Pfade",
        "12. Architekturdokumente & Vertragsspezifikationen",
        "13. Geschwisterwerkzeuge & Ökosystem-Matrix",
        "14. Testen, Verifikation & Qualitäts-Gates",
        "15. Sicherheitsrichtlinie & Meldewege (48h Antwort-SLA)",
        "16. Drittanbieter-Lizenzen & Level 1 SBOM",
        "17. Entdeckungs-Schlüsselwörter & KI-Agenten-Index",
        "18. Gesetzliche Hinweise, Haftungsbeschränkung & Lizenz (§ 521 BGB)",
    ]
    for pt in de_points:
        assert pt in readme_de, f"Missing German quick navigation point: {pt}"


def test_governance_invariants_table():
    """Verify 10-point Governance Invariants table in README.md and README_de.md."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "Governance & Runtime Invariants Matrix" in readme_en
    assert "Governance- & Laufzeit-Invarianten-Matrix" in readme_de

    invariants = [
        "100% Local-First & Zero-Egress",
        "Non-Elevation (RunAsInvoker)",
        "Immutable Event Ledger",
        "Atomic Reservation Integrity",
        "Fail-Closed Credit Gating",
        "Zero Cost for Inactive Runs (NO_WORK)",
        "Guaranteed Critical Exemption",
        "30-Day Receipt Retention",
        "Multi-OS Operating Parity",
        "Cloud Sync Directory Isolation",
    ]
    for inv in invariants:
        assert inv in readme_en, f"Invariant missing in README.md: {inv}"

    de_invariants = [
        "100% Local-First & Zero-Egress",
        "Non-Elevation (RunAsInvoker)",
        "Unveränderliches Event-Ledger",
        "Atomare Reservierungsintegrität",
        "Fail-Closed Credit Gating",
        "Null Kosten für Leerläufe (NO_WORK)",
        "Ausnahme-Garantie für Schutzläufe",
        "30-Tage Belegaufbewahrung",
        "Multi-OS Plattform-Parität",
        "Cloud-Sync-Ordner-Isolation",
    ]
    for inv in de_invariants:
        assert inv in readme_de, f"Invariant missing in README_de.md: {inv}"


def test_badges_consistency():
    """Verify badge presence for Ruff, 48h SLA, Pytest, Python, and Ecosystem."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for doc in (readme_en, readme_de):
        assert "ruff" in doc.lower()
        assert "pass" in doc.lower()
        assert "100%25" in doc
        assert "dev-bricks" in doc
        assert "open-bricks" in doc
        assert "48h" in doc
        assert "Third-Party" in doc or "Drittanbieter" in doc
        assert "Marketing" in doc


def test_security_slas_and_contacts():
    """Verify 48h Response SLA and 5-Day Triage commitment in SECURITY.md."""
    sec_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "48-Hour Response SLA" in sec_text
    assert "5-Day Triage Commitment" in sec_text
    assert "security@open-bricks.org" in sec_text
    assert "security@ellmos.ai" in sec_text
    assert "support@lukasgeiger.com" in sec_text
    assert "lukas@open-bricks.org" in sec_text


def test_ci_workflow_concurrency_and_compileall():
    """Verify CI workflow concurrency and bytecode verification."""
    ci_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "concurrency:" in ci_text
    assert "cancel-in-progress: true" in ci_text
    assert "python -m compileall -q src tests" in ci_text


def test_gitignore_conflict_and_lock_rules():
    """Verify .gitignore includes synchronization conflict and lock patterns."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "*.sync-conflict-*" in gitignore
    assert "*.conflict" in gitignore
    assert "LOCK.*" in gitignore
    assert "*.lock" in gitignore
    assert "LOCK*.txt" in gitignore


def test_local_marketing_log():
    """Verify local MARKETING-LOG.txt presence and valid entry."""
    m_log = REPO_ROOT / "MARKETING-LOG.txt"
    assert m_log.is_file(), "MARKETING-LOG.txt must exist in repo root"
    content = m_log.read_text(encoding="utf-8")
    assert "dev-bricks/automation-master" in content
    assert "PFAD_B_UPGRADE" in content


def test_changelog_recency():
    """Verify CHANGELOG.md contains the 2026-09-09 release entry."""
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "[0.1.1] - 2026-09-09" in changelog
    assert "Bilingual 14-Point Quick Navigation" in changelog


def test_gitignore_hygiene_patterns():
    """Verify .gitignore includes complete multi-host conflict and multi-agent lock patterns."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    required_patterns = [
        "*.sync-temp-*",
        "*-ASUS-GEI.*",
        "*-WORKSTATION-LG.*",
        "*-WORKSTATION.*",
        "LOCK",
        "LOCK.permissions.json",
        "uv.lock",
        "coverage/",
        "wheelhouse/",
        ".wheel-smoke/",
        "*.tmp",
        "*.bak",
        "*.swp",
        "*~",
        "*.log",
    ]
    for pat in required_patterns:
        assert pat in gitignore, f"Missing pattern in .gitignore: {pat}"


def test_pytest_configuration_and_flags():
    """Verify pyproject.toml standardizes pytest options to -ra -v and basetemp."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'addopts = "-ra -v --basetemp=.pytest_temp"' in pyproject
    assert 'pythonpath = ["src"]' in pyproject
    assert 'testpaths = ["tests"]' in pyproject


def test_ci_workflow_pytest_flags():
    """Verify CI workflow executes pytest -ra -v."""
    ci_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "pytest -ra -v" in ci_text
    assert "python -m compileall -q src tests" in ci_text
    assert "cancel-in-progress: true" in ci_text


def test_changelog_recent_entries():
    """Verify CHANGELOG.md has entries for 0.1.2 through 0.1.6 with standardized notes."""
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.1.6] - 2026-09-21" in changelog
    assert "## [0.1.5] - 2026-09-20" in changelog
    assert "## [0.1.4] - 2026-09-13" in changelog
    assert "## [0.1.3] - 2026-09-12" in changelog
    assert "## [0.1.2] - 2026-09-10" in changelog
    assert "PEP 561 Typing Marker" in changelog
    assert "Gitignore Hardening" in changelog
    assert "Bilingual 18-Point Quick Navigation" in changelog


def test_third_party_licenses_and_pep639():
    """Verify THIRD_PARTY_LICENSES.md presence, pure stdlib invariant, and PEP 639 config."""
    licenses_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert licenses_path.is_file(), "THIRD_PARTY_LICENSES.md must exist in repo root"
    content = licenses_path.read_text(encoding="utf-8")
    assert "Zero-Runtime-Dependency" in content or "Zero External Runtime Dependencies" in content
    assert "100% pure Python standard library" in content
    assert "pytest" in content
    assert "ruff" in content
    assert "setuptools" in content

    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'license = "MIT"' in pyproject
    assert 'License :: OSI Approved :: MIT License' not in pyproject
    expected_lf = (
        'license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", '
        '"THIRD_PARTY_LICENSES.txt"]'
    )
    assert expected_lf in pyproject


def test_todo_status_table_and_gate_readiness():
    """Verify TODO.md contains standard STATUS table and formalized tasks."""
    todo_path = REPO_ROOT / "TODO.md"
    assert todo_path.is_file(), "TODO.md must exist"
    todo_text = todo_path.read_text(encoding="utf-8")
    assert "## STATUS" in todo_text
    assert "| Category" in todo_text
    assert "Evidence / next gate" in todo_text
    assert "TASK-AM-" in todo_text


def test_final_gate_check_compliance():
    """Verify minimum ignore entries and absence of German indicators in English README."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for req in ["__pycache__", "*.pyc", ".env", "*.db", ".venv/", ".idea/", ".vscode/", "data/"]:
        assert req in gitignore, f"Missing required .gitignore entry for Gate 1: {req}"

    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    first_50 = "\n".join(readme_en.splitlines()[:50])
    # Gate 2 requires English language purity in first 50 lines
    assert "Dokumentation" not in first_50
    assert "Voraussetzungen" not in first_50


def test_target_personas_and_discoverability_contract():
    """Verify the 4 target personas and matrices across READMEs and MARKETING-LOG."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    marketing = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

    assert "Target Personas" in readme_en
    assert "Zielgruppen" in readme_de

    for p_id in ["[PERSONA-01]", "[PERSONA-02]", "[PERSONA-03]", "[PERSONA-04]"]:
        assert p_id in readme_en, f"Missing {p_id} in README.md"
        assert p_id in readme_de, f"Missing {p_id} in README_de.md"
        assert p_id in marketing, f"Missing {p_id} in MARKETING-LOG.txt"

    personas = [
        "Autonomous AI Agent Engineers",
        "DevOps, SRE & CI/CD Pipeline",
        "Edge, Embedded & Air-Gapped Systems Developers",
        "Enterprise Security",
    ]
    for persona in personas:
        assert persona in readme_en, f"Missing persona in README.md: {persona}"
        assert persona in marketing, f"Missing persona in MARKETING-LOG.txt: {persona}"

    assert "Autonome KI-Agenten-Entwickler" in readme_de
    assert "Unternehmens-Sicherheits- & Compliance-Verantwortliche" in readme_de


def test_third_party_licenses_audit_contract():
    """Verify THIRD_PARTY_LICENSES.md contains complete audit sections and invariant mappings."""
    licenses_path = REPO_ROOT / "THIRD_PARTY_LICENSES.md"
    assert licenses_path.is_file()
    content = licenses_path.read_text(encoding="utf-8")

    assert "2026-09-20" in content
    assert "2026-09-24" in content
    assert "2026-09-28" in content
    assert "2026-10-01" in content
    assert "Level 1 Software Bill of Materials (SBOM)" in content
    assert "Invariant Cross-Reference Matrix" in content
    assert "Zero External Runtime Dependencies" in content
    assert "PSF" in content
    assert "MIT License" in content
    assert "INV-LOCAL-01" in content
    assert "INV-ISOLAT-10" in content


def test_competitive_matrix_and_invariants_in_marketing_log():
    """Verify MARKETING-LOG.txt contains 5-way competitive matrix and invariants."""
    marketing = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

    assert "5-WAY COMPETITIVE DIFFERENTIATION MATRIX" in marketing
    assert "cron/systemd" in marketing
    assert "Airflow/Prefect" in marketing
    assert "AWS Budgets" in marketing
    assert "INV-LOCAL-01: 100% Local-First & Zero-Egress" in marketing
    assert "INV-ISOLAT-10: Cloud Sync Directory Isolation" in marketing
    assert "SIBLING ECOSYSTEM" in marketing
    assert "DevCenter" in marketing
    assert "CodeBox" in marketing


def test_pyproject_extended_urls():
    """Verify pyproject.toml [project.urls] contains extended resource links."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"Third-Party Licenses" =' in pyproject
    assert "THIRD_PARTY_LICENSES.md" in pyproject
    assert 'Notice =' in pyproject
    assert "NOTICE" in pyproject
    assert '"Marketing-Log" =' in pyproject
    assert "MARKETING-LOG.txt" in pyproject
    assert '"LLM-Ready" =' in pyproject
    assert "llms.txt" in pyproject


def test_governance_invariants_canonical_ids():
    """Verify canonical IDs INV-LOCAL-01 through INV-ISOLAT-10 appear in READMEs."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    expected_ids = [
        "INV-LOCAL-01",
        "INV-PRIV-02",
        "INV-IMMUT-03",
        "INV-ATOMIC-04",
        "INV-GATE-05",
        "INV-NOWORK-06",
        "INV-EXEMPT-07",
        "INV-RETENT-08",
        "INV-PARITY-09",
        "INV-ISOLAT-10",
    ]
    for inv_id in expected_ids:
        assert inv_id in readme_en, f"Missing {inv_id} in README.md"
        assert inv_id in readme_de, f"Missing {inv_id} in README_de.md"


def test_pep561_typing_marker_contract():
    """Verify PEP 561 py.typed marker exists and is packaged in pyproject.toml."""
    marker = REPO_ROOT / "src" / "automation_master" / "py.typed"
    assert marker.is_file(), "src/automation_master/py.typed must exist"

    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.setuptools.package-data]" in pyproject
    assert 'automation_master = ["py.typed"]' in pyproject


def test_cli_version_and_executable_module_contract():
    """Verify CLI --version, -v, and python -m automation_master module entrypoint."""
    import pytest

    from automation_master.cli import _parser, main

    parser = _parser()
    assert parser.prog == "automation-master"

    # Test parser version action
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0

    with pytest.raises(SystemExit) as exc_info:
        main(["-v"])
    assert exc_info.value.code == 0

    # Ensure __main__.py exists and is correctly configured
    main_py = REPO_ROOT / "src" / "automation_master" / "__main__.py"
    assert main_py.is_file(), "src/automation_master/__main__.py must exist"
    main_text = main_py.read_text(encoding="utf-8")
    assert "from .cli import main" in main_text
    assert "raise SystemExit(main())" in main_text


def test_ci_workflow_timeout_guardrail_contract():
    """Verify CI workflow defines a timeout guardrail for matrix test runs."""
    ci_file = REPO_ROOT / ".github" / "workflows" / "ci.yml"
    ci_text = ci_file.read_text(encoding="utf-8")
    assert "timeout-minutes: 15" in ci_text


def test_notice_attribution_contract():
    """Verify root NOTICE file exists and contains canonical attribution and license."""
    notice_path = REPO_ROOT / "NOTICE"
    assert notice_path.is_file(), "Root NOTICE file must exist"
    content = notice_path.read_text(encoding="utf-8")
    assert "automation-master" in content
    assert "Lukas Geiger" in content
    assert "dev-bricks" in content
    assert "open-bricks" in content
    assert "MIT License" in content


def test_statutory_disclaimer_521_bgb_contract():
    """Verify Section 18 statutory liability disclaimer (§ 521 BGB) in both READMEs."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "§ 521 BGB" in readme_en
    assert "Gefälligkeitsrecht" in readme_en or "unentgeltliche Zuwendung" in readme_en
    assert "Section 521 of the German Civil Code" in readme_en

    assert "§ 521 BGB" in readme_de
    assert "Gefälligkeitsrecht" in readme_de or "unentgeltliche Zuwendung" in readme_de
    assert "Bürgerlichen Gesetzbuches" in readme_de


def test_comparative_matrix_ten_dimensions_contract():
    """Verify 10-dimension comparative matrix vs 4 alternatives in READMEs."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for doc in (readme_en, readme_de):
        assert "cron/systemd" in doc
        assert "Airflow/Prefect" in doc
        assert "AWS Budgets" in doc
        assert "Local-First & Zero-Egress" in doc
        assert "BEGIN IMMEDIATE" in doc
        assert "NO_WORK" in doc


def test_mermaid_diagrams_semicolons_free():
    """Verify Mermaid blocks in README.md and README_de.md have zero trailing semicolons."""
    import re

    for filename in ("README.md", "README_de.md"):
        content = (REPO_ROOT / filename).read_text(encoding="utf-8")
        blocks = re.findall(r"```mermaid\s*\n(.*?)\n```", content, re.DOTALL)
        assert len(blocks) >= 2, f"At least 2 mermaid blocks required in {filename}"
        for idx, block in enumerate(blocks, 1):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            for line in lines:
                err_msg = f"Found trailing semicolon in {filename} block {idx}: {line}"
                assert not line.endswith(";"), err_msg


def test_welcome_and_stale_workflows_contract():
    """Verify welcome.yml and stale.yml exist with timeouts and least-privilege permissions."""
    welcome_file = REPO_ROOT / ".github" / "workflows" / "welcome.yml"
    assert welcome_file.is_file(), "welcome.yml must exist"
    welcome_text = welcome_file.read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in welcome_text
    assert "timeout-minutes: 5" in welcome_text
    assert "cancel-in-progress: true" in welcome_text
    assert "issues: write" in welcome_text
    assert "pull-requests: write" in welcome_text

    stale_file = REPO_ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_file.is_file(), "stale.yml must exist"
    stale_text = stale_file.read_text(encoding="utf-8")
    assert "actions/stale@v9" in stale_text
    assert "timeout-minutes: 10" in stale_text
    assert "cancel-in-progress: true" in stale_text
    assert "issues: write" in stale_text
    assert "pull-requests: write" in stale_text


def test_gitignore_cloud_sync_and_lock_defense_contract():
    """Verify .gitignore includes multi-host, lock system, and test scratch defense patterns."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    required = [
        "*-ASUS*",
        "*-LAPTOP*",
        "*-Mac Studio*",
        "*-MacBook*",
        "LOCK.user.*",
        "LOCK.until.*",
        "LOCK.condition.*",
        ".automation-lock",
        "!package-lock.json",
        ".pytest_temp/",
        ".hypothesis/",
        ".tox/",
    ]
    for pattern in required:
        assert pattern in gitignore, f"Missing defense pattern in .gitignore: {pattern}"


def test_pyproject_pytest_norecursedirs_and_freeze_contract():
    """Verify pyproject.toml pytest configuration and strict release version freeze."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'minversion = "7.0"' in pyproject
    assert "norecursedirs =" in pyproject
    assert '".git"' in pyproject
    assert '".pytest_cache"' in pyproject

    # Rule T-20260920-167562623: Pfad A/B runs must preserve frozen version
    assert f'version = "{automation_master.__version__}"' in pyproject
    assert automation_master.__version__ == "0.1.6"


def test_changelog_unreleased_section_contract():
    """Verify CHANGELOG.md contains an active [Unreleased] section for Pfad A changes."""
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [Unreleased]" in changelog
    assert "CI Workflow Provisioning & Hardening" in changelog
    assert "Multi-Host Conflict, Lock & Cache Defense" in changelog


def test_quick_navigation_dual_sec_anchors():
    """Verify reciprocal dual HTML anchors sec-01 through sec-18 in READMEs."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    for i in range(1, 19):
        anchor = f'<a id="sec-{i:02d}"></a>'
        assert anchor in readme_en, f"Missing {anchor} in README.md"
        assert anchor in readme_de, f"Missing {anchor} in README_de.md"


def test_ascii_four_view_topology_projection():
    """Verify ASCII four-view architectural topology projection in both READMEs."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    en_views = [
        "VIEW 1: CLIENT RUNTIMES & AGENT DRIVERS",
        "VIEW 2: AUTOMATION-MASTER CORE GOVERNANCE ENGINE",
        "VIEW 3: ATOMIC SQLite PERSISTENCE & CONCURRENCY",
        "VIEW 4: GOVERNANCE, SECURITY & PERIMETER",
    ]
    for view in en_views:
        assert view in readme_en, f"Missing {view} in README.md"

    de_views = [
        "SICHT 1: CLIENT-LAUFZEITEN & AGENTEN-TREIBER",
        "SICHT 2: AUTOMATION-MASTER KERN-GOVERNANCE-MOTOR",
        "SICHT 3: ATOMARE SQLite PERSISTENZ",
        "SICHT 4: GOVERNANCE, SICHERHEIT & PERIMETER",
    ]
    for view in de_views:
        assert view in readme_de, f"Missing {view} in README_de.md"


def test_pyproject_keywords_saturation_twenty():
    """Verify pyproject.toml defines exactly 20 saturated discoverability keywords."""
    import re
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r"keywords\s*=\s*\[(.*?)\]", pyproject_text, re.DOTALL)
    assert m is not None, "keywords list not found in pyproject.toml"
    raw_keywords = [k.strip(' \t\n\r",\'') for k in m.group(1).split(",") if k.strip(' \t\n\r",\'')]
    assert len(raw_keywords) == 20, (
        f"Expected exactly 20 keywords, got {len(raw_keywords)}: {raw_keywords}"
    )


def test_third_party_licenses_text_companion():
    """Verify plain-text Level 1 SBOM companion file THIRD_PARTY_LICENSES.txt."""
    txt_path = REPO_ROOT / "THIRD_PARTY_LICENSES.txt"
    assert txt_path.is_file(), "THIRD_PARTY_LICENSES.txt must exist in repo root"
    content = txt_path.read_text(encoding="utf-8")
    assert "automation-master" in content
    assert "Level 1 SBOM" in content
    assert "MIT License" in content
    assert "PSF-2.0" in content
    assert "INV-LOCAL-01" in content
    assert "INV-ISOLAT-10" in content
    assert "Zero-Copyleft Guarantee" in content
    assert "RunAsInvoker" in content


def test_auto_assign_and_label_sync_workflows_contract():
    """Verify auto-assign.yml and label-sync.yml exist with timeouts and permissions."""
    assign_file = REPO_ROOT / ".github" / "workflows" / "auto-assign.yml"
    assert assign_file.is_file(), "auto-assign.yml must exist"
    assign_text = assign_file.read_text(encoding="utf-8")
    assert "actions/github-script@v7" in assign_text
    assert "timeout-minutes: 5" in assign_text
    assert "cancel-in-progress: true" in assign_text
    assert "pull-requests: write" in assign_text
    assert "issues: write" in assign_text

    sync_file = REPO_ROOT / ".github" / "workflows" / "label-sync.yml"
    assert sync_file.is_file(), "label-sync.yml must exist"
    sync_text = sync_file.read_text(encoding="utf-8")
    assert "EndBug/label-sync@v2" in sync_text
    assert "timeout-minutes: 5" in sync_text
    assert "cancel-in-progress: true" in sync_text
    assert "issues: write" in sync_text
    assert ".github/labels.yml" in sync_text


def test_labels_yml_governance_contract():
    """Verify .github/labels.yml declares canonical 11 governance labels per GOVERNANCE.md §4.2."""
    labels_file = REPO_ROOT / ".github" / "labels.yml"
    assert labels_file.is_file(), ".github/labels.yml must exist"
    labels_text = labels_file.read_text(encoding="utf-8")
    expected_labels = [
        "bug",
        "enhancement",
        "good first issue",
        "help wanted",
        "documentation",
        "duplicate",
        "wontfix",
        "priority: high",
        "priority: low",
        "needs-triage",
        "stale",
    ]
    for label in expected_labels:
        assert f"name: {label}" in labels_text or f"name: '{label}'" in labels_text, (
            f"Missing canonical label: {label}"
        )


def test_contributing_bilingual_contract():
    """Verify CONTRIBUTING.md exists with bilingual sections, invariants, and quality gates."""
    contrib_file = REPO_ROOT / "CONTRIBUTING.md"
    assert contrib_file.is_file(), "CONTRIBUTING.md must exist in root"
    contrib_text = contrib_file.read_text(encoding="utf-8")
    assert "Contributing to automation-master" in contrib_text
    assert "#english" in contrib_text
    assert "#deutsch" in contrib_text
    assert "INV-LOCAL-01" in contrib_text
    assert "INV-PRIV-02" in contrib_text
    assert "INV-ISOLAT-10" in contrib_text
    assert "RunAsInvoker" in contrib_text
    assert "Plan D" in contrib_text
    assert "python -m compileall" in contrib_text
    assert "ruff check" in contrib_text
    assert "pytest -ra -v" in contrib_text


def test_pyproject_contributing_url_and_pytest_basetemp():
    """Verify pyproject.toml registers Contributing URL and pytest basetemp/norecursedirs."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    expected_url = (
        'Contributing = "https://github.com/dev-bricks/automation-master/blob/main/CONTRIBUTING.md"'
    )
    assert expected_url in pyproject
    assert '--basetemp=.pytest_temp' in pyproject
    assert '".pytest_temp"' in pyproject
    assert '".pytest_tmp*"' in pyproject
    assert '".hypothesis"' in pyproject
    assert '".tox"' in pyproject


def test_gitignore_extended_multi_host_and_lock_tokens():
    """Verify .gitignore includes multi-host tokens, canonical locks, and system artifacts."""
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    tokens = [
        "*-IDEAPAD*",
        "*-IDEAPAD-GEI*",
        "*_WORKSTATION*",
        "*_WORKSTATION-LG*",
        "LOCK.dev.*",
        "LOCK.antigravity.*",
        "LOCK.bugsearch.*",
        "*.swo",
        "Desktop.ini",
        "ehthumbs.db",
        "TASKPLAN_*.md",
    ]
    for token in tokens:
        assert token in gitignore, f"Missing token in .gitignore: {token}"


def test_third_party_licenses_audit_recency_20261001():
    """Verify THIRD_PARTY_LICENSES.md and text companion record 2026-10-01 audit recency."""
    md_content = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
    assert "2026-10-01" in md_content

    txt_content = (REPO_ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    assert "2026-10-01" in txt_content
    assert "Pfad A Re-Audit: 2026-10-01" in txt_content


def test_pfad_b_discoverability_audit_recency_20261003():
    """Verify 2026-10-03 Pfad B discoverability audit recency across docs and companions."""
    md_content = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
    assert "2026-10-03" in md_content
    assert "Pfad B Re-Audit: 2026-10-03" in md_content

    txt_content = (REPO_ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    assert "2026-10-03" in txt_content
    assert "Pfad B Re-Audit: 2026-10-03" in txt_content

    llms_txt = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "2026-10-03" in llms_txt

    m_log = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "8. PFAD B DISCOVERABILITY & RE-AUDIT (2026-10-03)" in m_log

    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    expected_entry = (
        "Pfad B Discoverability, Level 1 SBOM Re-Audit & Design Currency (2026-10-03)"
    )
    assert expected_entry in changelog


def test_pfad_b_discoverability_audit_recency_20261009():
    """Verify 2026-10-09 Pfad B discoverability audit recency across docs and notice."""
    md_content = (REPO_ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")
    assert "2026-10-09" in md_content
    assert "Pfad B Re-Audit: 2026-10-09" in md_content

    txt_content = (REPO_ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    assert "2026-10-09" in txt_content
    assert "Pfad B Re-Audit: 2026-10-09" in txt_content

    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Verified: 2026-10-09" in readme_en
    assert "Statutory Notice: § 521 BGB" in readme_en
    assert "107%20passed" in readme_en

    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")
    assert "Geprüft: 2026-10-09" in readme_de
    assert "Gesetzlicher Hinweis: § 521 BGB" in readme_de
    assert "107%20passed" in readme_de

    llms_txt = (REPO_ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "Last-checked: 2026-10-09" in llms_txt
    assert "107+ verified tests" in llms_txt

    m_log = (REPO_ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "9. PFAD B DISCOVERABILITY & RE-AUDIT (2026-10-09)" in m_log
    assert "Date: 2026-10-09" in m_log
    assert "REC-MKT-20261009-01" in m_log
    assert "REC-MKT-20261009-02" in m_log
    assert "REC-MKT-20261009-03" in m_log

    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    expected_entry = (
        "Pfad B Discoverability, Level 1 SBOM Re-Audit & Design Currency (2026-10-09)"
    )
    assert expected_entry in changelog
