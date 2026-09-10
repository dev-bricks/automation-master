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
    assert "Last-checked: 2026-09-10" in llms_text
    assert "0.1.2" in llms_text


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
    """Verify 14-point quick navigation exists in both README.md and README_de.md."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "### Quick Navigation" in readme_en
    assert "### Schnellnavigation" in readme_de

    en_points = [
        "1. Executive Summary",
        "2. System Architecture",
        "3. Reservation & Credit Governance Lifecycle",
        "4. Event Sourcing & Projection Lifecycle",
        "5. Safety Model & Governance Invariants",
        "6. Installation & Prerequisites",
        "7. CLI Usage & Operations",
        "8. Python API Integration",
        "9. Data Storage & Multi-OS Layout",
        "10. Sibling Tools & Ecosystem Matrix",
        "11. Architectural Contracts & Schema Specifications",
        "12. Security & Vulnerability Reporting",
        "13. License",
        "14. German Documentation / Deutsche Version",
    ]
    for pt in en_points:
        assert pt in readme_en, f"Missing English quick navigation point: {pt}"

    de_points = [
        "1. Übersicht & Management Summary",
        "2. Systemarchitektur",
        "3. Reservierungs- & Credit-Governance-Ablauf",
        "4. Event-Sourcing- & Projektionslebenszyklus",
        "5. Sicherheitsmodell & Governance-Invarianten",
        "6. Installation & Voraussetzungen",
        "7. CLI-Bedienung & Betrieb",
        "8. Python-API-Integration",
        "9. Datenspeicher & Multi-OS-Pfade",
        "10. Geschwisterwerkzeuge & Ökosystem-Matrix",
        "11. Architekturdokumente & Vertragsspezifikationen",
        "12. Sicherheitsrichtlinie & Meldewege",
        "13. Lizenz",
        "14. Englische Dokumentation / English Version",
    ]
    for pt in de_points:
        assert pt in readme_de, f"Missing German quick navigation point: {pt}"


def test_governance_invariants_table():
    """Verify 10-point Governance Invariants table in README.md and README_de.md."""
    readme_en = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (REPO_ROOT / "README_de.md").read_text(encoding="utf-8")

    assert "## Safety Model & Governance Invariants" in readme_en
    assert "## Sicherheitsmodell & Governance-Invarianten" in readme_de

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
        assert "63%20passed" in doc
        assert "100%25" in doc
        assert "dev-bricks" in doc
        assert "open-bricks" in doc
        assert "48h" in doc


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
    """Verify pyproject.toml standardizes pytest options to -ra -v."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'addopts = "-ra -v"' in pyproject
    assert 'pythonpath = ["src"]' in pyproject
    assert 'testpaths = ["tests"]' in pyproject


def test_ci_workflow_pytest_flags():
    """Verify CI workflow executes pytest -ra -v."""
    ci_text = (REPO_ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "pytest -ra -v" in ci_text
    assert "python -m compileall -q src tests" in ci_text
    assert "cancel-in-progress: true" in ci_text


def test_changelog_recent_pfad_a_entry():
    """Verify CHANGELOG.md has a Pfad A entry for 0.1.2 with standardized hygiene notes."""
    changelog = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "## [0.1.2] - 2026-09-10" in changelog
    assert "Gitignore Hardening" in changelog
    assert "Standardized Pytest & CI Configuration" in changelog
