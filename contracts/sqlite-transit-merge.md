# SQLite-Transit merge contract v1

The `events` table is an immutable grow-only set with semantic identity checks.
A merge inserts missing rows, counts exact duplicates as unchanged, reports
zero updates, and aborts if an event ID or dedupe key maps to different content.

Input snapshots must be closed and verified by `sqlite-transit-sync`. Clock
timestamps are retained as evidence but never choose a winner. Stale snapshots
are safe because later merges add the remaining immutable events.

The adapter consumes the public `sqlite-transit-sync` `Snapshot` shape
(`node_id`, `path`) and returns its public `MergeReport` shape
(`snapshot` as the snapshot file name, `source_node`, list-valued
`skipped_tables`). Tests must not substitute incompatible field names.
