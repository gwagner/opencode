---
name: api-contract-conformance-testing
description: Implements focused conformance tests for approved API request, response, error, and compatibility contracts.
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
  - approved API contract
  - selected endpoint inventory
  - safe API test target
  - caller-provided permitted API authority source and test paths
  - caller-provided permitted database fixture contract path when deterministic application state is required
compatibility: opencode
metadata:
  domain: api-testing
  phase: contract-conformance
---

# API contract conformance testing

## Inputs

Require an approved API contract, selected endpoint inventory, safe API test target, caller-provided permitted API authority, source, and test paths, and a caller-provided permitted database fixture contract path when deterministic application state is required. A machine-readable contract is preferred; otherwise use an approved field-level contract. Stop when no authoritative contract exists.

## Dead-code rule

Within the approved affected test scope, remove unused test helpers and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in tests. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "Focused API conformance tests and validation result"
workflow:
  - id: "database-fixture"
    when: "After contract tests are implemented when execution requires deterministic application database state."
    skill: "non-production-database-fixture"
  - id: "validate-project"
    when: "After API contract conformance tests and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inspect the approved machine-readable or field-level contract, selected endpoint inventory, implementation evidence from API discovery, existing API tests, test client, fixtures, and safe target. Stop with `blocked` if authority is absent or conflicts internally.
2. Build one endpoint matrix. For each selected `METHOD PATH`, record authentication class, parameters, request content type/schema, successful statuses/headers/schema, documented error statuses/schema, and compatibility constraints.
3. Compare implementation and authority before writing tests. Record every mismatch separately; never silently update the contract or application to erase evidence.
4. Implement deterministic contract tests using existing clients and test-owned resources. Assert method, path, parameter location, requiredness, content type, explicit response-field allowlist, field type, nullability, enum values, status, required headers, stable machine error code, and safe error shape when authority defines them.
5. Add negative leakage assertions for persistence-only, provider, credential, secret-adjacent, and internal diagnostic fields. Preserve approved semantic distinctions among absent, unavailable, zero, empty, accepted, delivered, and failed.
6. For changed compatibility-sensitive contracts, exercise both permitted existing-client payloads and the changed contract when fixtures establish them. Test removal, requiredness, type, enum, and response-field changes only where the compatibility policy defines an expectation.
7. Keep endpoint setup isolated. Use stable values, avoid volatile timestamps/identifiers unless the contract defines them, and never test against production or a shared mutable target.
8. Use `project-validation` to run focused endpoint tests, then the relevant contract suite when safe. Classify findings as contract mismatch, implementation defect, test defect, safe-target blocker, authority blocker, or pre-existing failure. Do not alter application behavior solely to pass a test.

## Required report

Report the endpoint matrix, contract source/version, implementation mismatches, test paths, commands, result per endpoint, compatibility coverage, skipped rows, and blockers.
