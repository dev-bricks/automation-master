# SQLite-Transit merge contract v1

The `events` table is an immutable grow-only set with semantic identity checks.
A merge inserts missing rows, counts exact duplicates as unchanged, reports
zero updates, and aborts if an event ID or dedupe key maps to different content.

Input snapshots must be closed and verified by `sqlite-transit-sync`. Clock
timestamps are retained as evidence but never choose a winner. Stale snapshots
are safe because later merges add the remaining immutable events.
