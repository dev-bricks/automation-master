# Provider prompt repair contract v1

This is an adapter seam for Automation Health. The core now provides a pure
in-memory verifier in `automation_master.adapters.prompt_repair`; it does not
open, edit, replace, validate, or activate provider configuration. The
verifier grants no provider-mutation authority by itself.

## Preconditions

- provider and configuration format are explicitly supported;
- exact automation identity and configuration path are resolved;
- configuration is readable and parseable;
- expected pre-change content hash matches;
- requested change is limited to the prompt;
- a recoverable byte-exact backup destination is available.

## Invariants

The adapter must prove that these fields are unchanged:

- model;
- thinking/reasoning level;
- schedule;
- enabled/status state;
- execution target;
- working directory.

Provider-specific additional invariants are allowed. A generic text or TOML
search-and-replace is not a valid proof.

## Transaction

1. Create and hash a byte-exact backup.
2. Parse the provider configuration.
3. Apply a bounded prompt-only edit.
4. Serialize to a staged file and produce a small redacted diff.
5. Run provider-specific validation.
6. Atomically replace the original configuration.
7. Read back, parse again, and verify every invariant.
8. On any mismatch, restore the backup and verify rollback.
9. Emit an immutable receipt containing hashes, provider, automation ID,
   validation result, rollback state, and a secret-free diff summary.

Antigravity-style self-healing uses the same transaction through a dedicated
contract adapter (`AntigravityPromptRepairContractAdapter`). Unsupported or
ambiguous configurations fail closed and remain manual. Actual provider
mutation remains a future, separately authorized capability.
