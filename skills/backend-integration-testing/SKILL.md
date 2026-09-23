---
name: backend-integration-testing
description: Implements focused tests for changed backend use cases, persistence, adapters, jobs, and error mapping.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    non-production-database-fixture: allow
    project-validation: allow
inputs:
  - approved backend contract
  - caller-provided permitted backend authority source and test paths
  - project test infrastructure
  - caller-provided permitted database fixture contract path when deterministic application state is required
compatibility: opencode
metadata:
  domain: backend-testing
  phase: implementation
---

# Backend integration testing

## Inputs

Require an approved backend contract, caller-provided permitted backend authority, source, and test paths, project test infrastructure, and a caller-provided permitted database fixture contract path when deterministic application state is required. Stop when an external dependency cannot be isolated safely.

## Dead-code rule

Within the approved affected test scope, remove unused test helpers and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in tests. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "Focused backend integration tests and validation result"
workflow:
  - id: "database-fixture"
    when: "After affected tests are implemented when execution requires deterministic application database state."
    skill: "non-production-database-fixture"
  - id: "validate-project"
    when: "After backend integration tests and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inspect approved backend contract, changed use cases, persistence paths, adapters, jobs, error types, existing integration tests, and safe local dependency setup. Do not introduce a competing test framework.
2. Build an affected-invariant matrix with one row per changed use case or read: input/precondition, owning boundary, expected result, persistence effect, external effect, typed failure, ordering, concurrency, idempotency, tenant scope, and cleanup owner.
3. Choose the narrowest harness that can falsify each invariant. Use fakes through production ports for orchestration, clocks, randomness, queues, and provider failures. Use an isolated real database for constraints, ownership joins, rollback, total ordering, page boundaries, leases, races, stale owners, duplicate completion, and concurrent workers.
4. Create deterministic, test-owned records and dependencies only through the approved shared test lifecycle. Do not create feature-owned allocation, migration, seed, reset, identity, clock, cleanup, or external-effect infrastructure. Never mutate production or shared environments; report `blocked` when isolation is unproven.
5. Implement success and specified failure tests for every matrix row. Where applicable, inject mid-transaction failure and exercise duplicate, restart, stale-owner, concurrent-worker, and later-configuration-change paths.
6. For reads, polling, streams, fragments, detail views, and diagnostics, assert state equality and zero unapproved provider, audit, session, retention, attempt, health, retry, or row-lock effects across repeated reads.
7. For projections and errors, assert explicit field allowlists, safe typed error mapping, bounded redacted diagnostics, semantic null/unavailable distinctions, and absence of persistence-only or provider fields.
8. For ordered collections, assert the complete persisted total order before slicing and test equal-primary-key page boundaries, refresh, retry, and traversal.
9. For changed diagnostics, assert approved fields, stable outcomes, bounded samples, explicit truncation, low-cardinality labels, expected-no-work classification, redaction, and non-recursive recorder failure where applicable.
10. For a frontend interaction-log ingestion command, test authentication, authorization, request protection, content type, schema version, event and field allowlists, request and batch bounds, field limits, timestamp handling, rate limits, duplicate behavior, and no-store non-reflective responses. Assert client-selected trusted context is discarded, prohibited data is rejected or removed before emission, server-owned context is added only when permitted, accepted events reach the structured application logger exactly as specified, logger failure is non-recursive, and rejected telemetry cannot alter domain state or the originating user workflow.
11. Verify cleanup: test-owned records, files, queues, and fakes must not leak into later tests. Do not delete records outside the attested test scope.
12. Use `project-validation` to run focused tests, then the relevant existing integration suite when safe. Classify failures as test defect, implementation defect, authority mismatch, dependency/infrastructure blocker, or pre-existing failure.

## Required report

Report the invariant matrix, isolation mechanism, test paths, commands, outcomes, omitted rows with rationale, and blockers.
