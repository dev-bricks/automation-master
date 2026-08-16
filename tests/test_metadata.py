from __future__ import annotations

import json
from pathlib import Path

import automation_master

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_version_parity():
    """Verify version parity across pyproject.toml, package, and manifest."""
    pyproject_text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{automation_master.__version__}"' in pyproject_text

    manifest = json.loads((REPO_ROOT / "ellmos-module.v2.json").read_text(encoding="utf-8"))
    assert manifest["version"] == automation_master.__version__

    changelog_text = (REPO_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"## {automation_master.__version__}" in changelog_text


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
    assert "Last-checked:" in llms_text
