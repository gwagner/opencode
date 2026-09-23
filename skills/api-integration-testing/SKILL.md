---
name: api-integration-testing
description: Builds maintainable API integration tests using existing project infrastructure for contracts, access control, validation, CRUD flows, and isolation.
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
  - api-discovery output
  - established endpoint contract
  - safe test target
  - caller-provided permitted API authority source and test paths
  - caller-provided permitted database fixture contract path when deterministic application state is required
compatibility: opencode
metadata:
  domain: api-testing
  phase: implementation
---

# API integration testing

## Inputs

Require API-discovery output, an established endpoint contract, a safe test target, caller-provided permitted API authority, source, and test paths, and a caller-provided permitted database fixture contract path when deterministic application state is required.

## Dead-code rule

Within the approved affected test scope, remove unused test helpers and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in tests. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "Maintainable API integration tests for an established endpoint contract"
workflow:
  - id: "database-fixture"
    when: "After selected API tests are implemented when execution requires deterministic application database state."
    skill: "non-production-database-fixture"
  - id: "validate-project"
    when: "After all selected post-change stages."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

Use only after the caller supplies `api-discovery` output establishing the endpoint contract and authentication model.

## Implementation

1. Reuse the project's test framework, location, client, fixtures, configuration, formatting, and lint conventions. Introduce no competing framework.
2. Cover the relevant baseline:
   - Public: unauthenticated success.
   - Authenticated: missing and invalid credentials rejected; valid credentials succeed.
   - Authorized: unauthenticated and authenticated-unauthorized requests rejected; authorized request succeeds.
3. Assert stable contract behavior: status, content type, required headers, explicit response-field allowlist, field types, nullability, response schema, and documented safe error shape. Preserve approved distinctions among absent, unavailable, zero, empty, accepted, delivered, and failed. For user-facing flows, cover documented success, failure, and recovery. Avoid volatile literals unless guaranteed.
4. Add prioritized negative cases for required fields, malformed values, enums, parameters, content types, and missing resources. Avoid combinatorial expansion before baseline coverage.
5. For each read, refresh, poll, stream, fragment, detail, retry-status, or diagnostic endpoint, compare state before and after repeated requests and assert zero unapproved provider calls, sends, attempts, session refreshes, audit appends, retention extensions, retry-state changes, or command-style locks.
6. For CRUD, create unique test data, exercise the isolated lifecycle, verify effects, and clean up owned resources. Do not depend on arbitrary records or execution order.
7. Any deterministic application database state must use the approved shared test lifecycle. Do not create feature-owned allocation, migration, seeding, clock, identity, reset, or cleanup paths. Report `blocked` when no safe lifecycle exists.
8. Keep environment values configurable and reuse test-safe dependencies. Never embed credentials or redirect tests to production.
9. Extract helpers only when they remove meaningful repetition.

## Safe execution

Never truncate arbitrary data, drop schemas, delete unrelated records, modify production configuration, run destructive migrations, or mutate a production endpoint. If a safe target cannot be established, write useful tests, skip unsafe execution, and report the blocker.

Use `project-validation` to format and run the narrowest relevant tests, then broader integration checks when safe. Classify failures as test defect, implementation defect, contract mismatch, or environment blocker. Fix test defects; preserve meaningful failures and never change application behavior solely to make tests pass unless explicitly requested.
