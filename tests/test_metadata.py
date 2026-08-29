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
    assert "automation.runtime.observe" in manifest["provides"]
    assert "automation.runtime.receipt" in manifest["provides"]
    assert "automation.runtime.statistics" in manifest["provides"]
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
        "contracts/automation-runtime-observation.md",
        "contracts/automation-runtime-observation_de.md",
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
        "AutomationRuntime",
        "RuntimeReceiptStore",
        "read_provider_receipt",
        "read_scheduler_run",
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
    assert "AutomationRuntime" in llms_text
    assert "runtime-provider-readback" in llms_text
    assert "ARCHITECTURE.md" in llms_text
    assert "Last-checked: 2026-08-29" in llms_text


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
        assert "AutomationRuntime" in readme


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


