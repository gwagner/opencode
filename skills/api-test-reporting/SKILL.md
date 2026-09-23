---
name: api-test-reporting
description: Reports API integration-test coverage, execution, contract and access-control findings, blockers, and prioritized remaining work.
classification: non-technical
opencode_permission:
  read: allow
  skill:
    api-discovery: allow
inputs:
  - API discovery or execution results
  - caller-provided permitted endpoint coverage evidence paths
compatibility: opencode
metadata:
  domain: api-testing
  phase: reporting
---

# API integration-test reporting

## Inputs

Require API discovery or execution results and caller-provided permitted endpoint coverage evidence paths.

## Deterministic workflow

```yaml
request: "Concise API integration-test coverage and execution report"
workflow:
  - id: "discover-api"
    when: "Before reporting when API discovery has not already established the inspected contract."
    skill: "api-discovery"
```

Use after API discovery or integration-test execution.

Report concisely:

- Specification sources, implementation framework, access-control mechanisms, and test infrastructure inspected.
- Endpoint totals and coverage by public, authenticated, authorized, tenant-owned, nested-resource, read, and command classification; use `covered`, `partial`, `failing`, `blocked`, or `not started`.
- Significant test, fixture, and helper files created or changed.
- Exact commands executed with passing, failing, skipped, and blocked results.
- Separate specification mismatches, authentication issues, tenant-source or ownership-graph issues, nondisclosure failures, read-side effects, projection/error leakage, resilience issues, corrected test defects, and environment blockers.
- State material user-task outcomes covered or still at risk when the endpoints support a user-facing flow.
- Risk-prioritized remaining endpoint, mismatch-matrix, access-state, read-purity, validation, CRUD, resilience, and edge-case work.

Distinguish tests implemented, executed, and passed. Never claim execution or coverage from generated source alone, and do not clutter the report with unrelated or temporary files.
