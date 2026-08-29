# TODO

## Before real activation

- Run a real, read-only provider-and-scheduler receipt pilot outside OneDrive;
  the runtime observer and synthetic acceptance coverage are implemented, but a
  production-native evidence source has not yet been authorized.
- Add provider-specific JSON selectors only for verified native receipt
  formats; keep unknown layouts fail-closed.
- Run a 14-day synthetic-to-shadow pilot on workstation and laptop.
- Calibrate reward weights and credit conversion from receipts.
- Review trust allowlists and signed manifest provenance.
- Integrate the credit gate into an isolated scheduler feature flag.
- Register the custom merge policy in `sqlite-transit-sync`.
- Define retention for detailed receipts while preserving audit hashes. Done in
  `contracts/receipt-retention.md` via a read-only 30-day projection that keeps
  immutable event metadata and `payload_hash`.
- Add operator review and explicit versioned policy override UI.
- Confirm monitoring, rollback drill, and recovery point objectives.
- Implement provider-specific Automation Health prompt-repair adapters:
  backup, prompt-only small diff, invariant check for model/thinking/schedule/
  status/target/CWD, provider validation, readback, rollback, and receipt.
- Add a contract test adapter for an Antigravity-style prompt self-healing
  pattern before enabling any provider mutation. Done as a pure, fail-closed
  verifier in `automation_master.adapters.prompt_repair`; provider mutation is
  still not enabled.

No item above authorizes publication, GitHub provisioning, or hard enforcement.
