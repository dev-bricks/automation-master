# Receipt retention policy v1

The event ledger is append-only. Receipt retention is a read-only projection
policy; it does not update or delete SQLite events and does not change the
receipt payload hash.

## Classes

- `detailed`: the default 30-day hot window. The receipt's `details` mapping is
  available together with its safe event metadata, run ID, outcome, and useful
  flag.
- `audit-summary`: events older than the cutoff. The detail mapping is omitted,
  while event ID, node, budget epoch, entity identity, timestamp, event version,
  tombstone state, and the original `payload_hash` remain available together
  with run ID, outcome, and useful.

The cutoff is evaluated in UTC using an explicitly supplied comparison time.
An event exactly on the cutoff remains detailed; future-dated events remain
detailed until they age past the window. Invalid or timezone-less timestamps,
malformed receipt fields, and non-receipt events fail closed.

## Scope and safety

`project_receipt` and `project_receipts` return derived dictionaries and never
mutate their input events or the `EventStore`. Long-term archival and deletion
of detail payloads, if ever authorized, must happen outside the core ledger
through a separately reviewed storage policy. Audit consumers can verify the
source payload using the retained `payload_hash`.
