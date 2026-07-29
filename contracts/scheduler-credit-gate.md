# Scheduler credit gate v1

Input fields: stable run ID, budget epoch, scope, work-item ID, work
availability, requested credits, run class, and minimum-coverage flag.

Output fields: status, run ID, optional reservation ID, credits,
available-before value, and explanation.

The scheduler must:

1. call the gate before launching work;
2. treat `NO_WORK` and `BUDGET_DENIED` as no-launch outcomes;
3. submit exactly one receipt for an allowed run;
4. keep the same run ID across retries.
5. acquire and retain its own scheduler lease before launching any automation
   registered as `globally-single-writer`; the credit gate is not a lease and
   never replaces scheduler claim/heartbeat semantics.

The adapter does not decide when a run should occur and cannot start a process.
