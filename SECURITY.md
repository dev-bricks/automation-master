# Security

## Trust defaults

- Visibility is private.
- Runtime network access is not required.
- Deployment activation is denied unless a local trust policy allows it.
- The default System-Gap trust policy trusts no source, no target root, and
  only `disabled` or `shadow` modes.
- Manifest hash and version are checked before import.
- Downgrades and foreign target nodes are rejected.

## Data handling

The event payload belongs to the local application and may contain operational
metadata. Do not put credentials, contact details, payment data, or raw private
documents into event payloads. Diagnostic export helpers expose metadata and
payload hashes, not raw payloads, and reject common credential patterns.

Databases must stay outside OneDrive or other file-level synchronization
folders. Replication should use a verified closed SQLite snapshot through
`sqlite-transit-sync`.

## Concurrency and recovery

Local reservations are atomic. Cross-host operation is eventually consistent,
using independently assigned envelopes. A payload hash mismatch, duplicate
identity with different content, stale manifest, or untrusted deployment plan
fails closed.

Rollback disables activation and restores the previously verified module
version. Ledger history is not rewritten during rollback.

Report security issues privately; do not open a public issue containing event
payloads or local paths.
