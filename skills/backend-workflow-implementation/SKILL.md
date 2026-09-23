---
name: backend-workflow-implementation
description: Implements one approved state-changing backend workflow with explicit atomicity, concurrency, idempotency, snapshot, and recovery behavior.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    project-validation: allow
inputs:
  - approved state-changing use-case contract
  - caller-provided permitted source and test paths
  - established boundary and transaction design
  - applicable concurrency idempotency snapshot and recovery rules
  - project-native validation context
---

# Backend workflow implementation

## Inputs

Require an approved state-changing use-case contract, caller-provided permitted source and test paths, established boundary and transaction design, applicable concurrency, idempotency, snapshot and recovery rules, and project-native validation context.

Use only for a completed backend command, job, or worker workflow. Use a scaffold procedure for intentionally incomplete behavior and a generic change procedure for changes without state transitions.

## Dead-code rule

Within the approved affected source and test scope, remove unused functions and modules, commented-out code, and logic kept only for reference. Use version-control history for reference; preserve uncertain live behavior and report it rather than guessing.

## Deterministic workflow

```yaml
request: "One correctly implemented state-changing backend workflow"
workflow:
  - id: validate-project
    when: "After implementation and every selected post-change check."
    skill: project-validation
    report:
      - passed
      - failed
      - skipped
      - blocked
```

## Procedure

1. Confirm the approved command, actor, inputs, preconditions, state transition, observable result, failures, and caller-established ports. Stop when material behavior or transaction ownership is unresolved.
2. Name one application transaction owner. Inventory every action-owned state, audit, event, queue, snapshot, session, and scheduling effect. Commit them together or prove why an effect occurs after commit; on failure, verify the approved rollback behavior.
3. For concurrent or retryable work, define the durable ownership record, opaque claim or version token, lease or stale-owner behavior, deterministic idempotency identity, duplicate-completion result, and restart or crash recovery. Mark inapplicable rows with evidence rather than silently omitting them.
4. For delayed work, capture every authority-required event-time value before enqueue or handoff. Retries must use that immutable snapshot and stable event identity rather than later mutable configuration.
5. Implement through established application-facing ports and composition wiring. Keep transport, persistence, framework, and provider details in their owning adapters.
6. Add focused tests that can falsify each applicable invariant: successful commit, injected mid-transaction failure, duplicate request or completion, stale owner, concurrent claimant, restart, and later-configuration change. Use the real invariant-owning boundary when a fake cannot prove the behavior.
7. Do not create ad hoc database allocation, seeding, reset, clock, identity, cleanup, or external-effect infrastructure. If deterministic state lacks an approved safe lifecycle, report `blocked`.
8. Report transaction ownership, effect inventory, applicability decisions, changed paths, focused evidence, validation result, and blockers.

## Audit criterion

A changed stateful workflow is nonconforming when an applicable transaction, rollback, concurrency, duplicate, snapshot, or recovery rule lacks executable evidence at the boundary that owns it.
