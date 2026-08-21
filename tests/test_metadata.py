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
    assert "ARCHITECTURE.md" in llms_text
    assert "Last-checked: 2026-08-21" in llms_text


def test_security_policy_bilingual_and_contacts():
    """Verify that SECURITY.md contains bilingual sections and valid contact emails."""
    sec_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "English: Security & Trust Model" in sec_text
    assert "Deutsch: Sicherheitsrichtlinie" in sec_text
    assert "security@ellmos.ai" in sec_text
    assert "support@lukasgeiger.com" in sec_text
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


def test_pyproject_classifiers_and_settings():
    """Verify python 3.10-3.13 classifiers and dev dependencies."""
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'Programming Language :: Python :: 3.10' in pyproject
    assert 'Programming Language :: Python :: 3.11' in pyproject
    assert 'Programming Language :: Python :: 3.12' in pyproject
    assert 'Programming Language :: Python :: 3.13' in pyproject
    assert 'pytest' in pyproject
    assert 'ruff' in pyproject
