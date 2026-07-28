"""Bounded export helpers that keep event payloads local by default."""

from __future__ import annotations

import re
from typing import Any

from .store import Event

_SENSITIVE = re.compile(
    r"(?i)(?:bearer\s+[a-z0-9._-]{12,}|"
    r"(?:api[_-]?key|password|secret|token)\s*[:=]\s*\S+|"
    r"\b(?:sk|ghp|github_pat)_[a-z0-9_-]{12,})"
)


def contains_sensitive_text(value: Any) -> bool:
    if isinstance(value, dict):
        return any(
            contains_sensitive_text(key) or contains_sensitive_text(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple, set)):
        return any(contains_sensitive_text(item) for item in value)
    return bool(_SENSITIVE.search(str(value)))


def safe_event_metadata(event: Event) -> dict[str, Any]:
    """Return non-payload metadata suitable for diagnostics and health reports."""

    return {
        "event_id": event.event_id,
        "node_id": event.node_id,
        "budget_epoch": event.budget_epoch,
        "event_type": event.event_type,
        "entity_type": event.entity_type,
        "entity_id": event.entity_id,
        "event_version": event.event_version,
        "created_at": event.created_at,
        "tombstone": event.tombstone,
        "payload_hash": event.payload_hash,
    }


def require_export_safe(payload: Any) -> None:
    if contains_sensitive_text(payload):
        raise ValueError("export rejected: payload resembles a credential or secret")
