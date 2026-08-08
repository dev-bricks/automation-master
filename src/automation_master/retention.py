"""Deterministic receipt-retention projections.

The event ledger remains append-only.  Retention only controls which receipt
fields a downstream view exposes: detailed payloads stay in a bounded hot
window while event identity and the immutable payload hash remain available in
the audit summary indefinitely.  This module never updates or deletes rows.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any

from .security import safe_event_metadata
from .store import Event


class ReceiptRetentionClass(str, Enum):
    """Projection class selected for a receipt event."""

    DETAILED = "detailed"
    AUDIT_SUMMARY = "audit-summary"


@dataclass(frozen=True)
class ReceiptRetentionPolicy:
    """Retention policy for immutable receipt projections.

    ``detailed_days`` is measured from the event's timezone-aware
    ``created_at`` timestamp.  Events on the cutoff remain detailed; older
    events become audit summaries.  A negative window is invalid.
    """

    detailed_days: int = 30

    def __post_init__(self) -> None:
        if (
            isinstance(self.detailed_days, bool)
            or not isinstance(self.detailed_days, int)
            or self.detailed_days < 0
        ):
            raise ValueError("detailed_days must be a non-negative integer")

    def classify(self, created_at: str, *, now: datetime) -> ReceiptRetentionClass:
        """Classify a receipt at an explicitly supplied UTC comparison time."""

        created = _parse_aware_datetime(created_at)
        current = _normalise_now(now)
        cutoff = current - timedelta(days=self.detailed_days)
        if created >= cutoff:
            return ReceiptRetentionClass.DETAILED
        return ReceiptRetentionClass.AUDIT_SUMMARY


def project_receipt(
    event: Event,
    *,
    policy: ReceiptRetentionPolicy,
    now: datetime,
) -> dict[str, Any]:
    """Project one receipt while preserving its immutable audit metadata.

    Only ``details`` is removed from an old receipt.  The event's original
    ``payload_hash`` is copied untouched by :func:`safe_event_metadata`, so a
    consumer can still verify the source event without retaining its detail
    payload in the hot projection.
    """

    if event.event_type != "RECEIPT_RECORDED":
        raise ValueError("receipt retention accepts only RECEIPT_RECORDED events")
    if not isinstance(event.payload, Mapping):
        raise ValueError("receipt payload must be a mapping")

    payload = event.payload
    run_id = payload.get("run_id", event.entity_id)
    outcome = payload.get("outcome")
    useful = payload.get("useful")
    details = payload.get("details", {})
    if not isinstance(run_id, str) or not run_id.strip():
        raise ValueError("receipt run_id must be a non-empty string")
    if not isinstance(outcome, str) or not outcome.strip():
        raise ValueError("receipt outcome must be a non-empty string")
    if not isinstance(useful, bool):
        raise ValueError("receipt useful must be boolean")
    if not isinstance(details, Mapping):
        raise ValueError("receipt details must be a mapping")

    retention_class = policy.classify(event.created_at, now=now)
    projected = safe_event_metadata(event)
    projected.update(
        {
            "schema": "automation-master.receipt-retention.v1",
            "run_id": run_id,
            "outcome": outcome,
            "useful": useful,
            "retention_class": retention_class.value,
            "details_retained": retention_class is ReceiptRetentionClass.DETAILED,
            "details": deepcopy(dict(details))
            if retention_class is ReceiptRetentionClass.DETAILED
            else None,
        }
    )
    return projected


def project_receipts(
    events: Sequence[Event],
    *,
    policy: ReceiptRetentionPolicy,
    now: datetime,
) -> list[dict[str, Any]]:
    """Project a sequence without mutating the source events or store."""

    return [project_receipt(event, policy=policy, now=now) for event in events]


def _normalise_now(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError("now must be a timezone-aware datetime")
    return value.astimezone(timezone.utc)


def _parse_aware_datetime(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("created_at must be a non-empty ISO timestamp")
    normalised = value.strip()
    if normalised.endswith("Z"):
        normalised = f"{normalised[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(normalised)
    except ValueError as exc:
        raise ValueError("created_at must be a valid ISO timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("created_at must include a timezone")
    return parsed.astimezone(timezone.utc)


__all__ = [
    "ReceiptRetentionClass",
    "ReceiptRetentionPolicy",
    "project_receipt",
    "project_receipts",
]
