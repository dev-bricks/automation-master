import json
from pathlib import Path

import pytest

from automation_master.security import contains_sensitive_text, require_export_safe


def test_secret_like_payload_is_rejected():
    assert contains_sensitive_text({"token": "token=abc123456789012345"})
    with pytest.raises(ValueError):
        require_export_safe({"authorization": "Bearer abcdefghijklmnop"})
    require_export_safe({"run_id": "synthetic-1", "status": "NO_WORK"})


def test_synthetic_pilot_has_two_families_and_two_hosts():
    fixture = (
        Path(__file__).parents[1] / "examples" / "pilot-two-hosts.json"
    ).read_text(encoding="utf-8")
    pilot = json.loads(fixture)
    assert pilot["mode"] == "shadow"
    assert len(pilot["hosts"]) == 2
    assert len(pilot["families"]) == 2
    assert all(len(family["variants"]) == 2 for family in pilot["families"])
