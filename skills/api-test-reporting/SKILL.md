---
name: api-test-reporting
description: Reports API integration-test coverage, execution, contract and access-control findings, blockers, and prioritized remaining work.
compatibility: opencode
metadata:
  domain: api-testing
  phase: reporting
---

# API integration-test reporting

Use after API discovery or integration-test execution.

Report concisely:

- Specification sources, implementation framework, access-control mechanisms, and test infrastructure inspected.
- Endpoint totals and coverage by public, authenticated, and authorized classification; use `covered`, `partial`, `failing`, `blocked`, or `not started`.
- Significant test, fixture, and helper files created or changed.
- Exact commands executed with passing, failing, skipped, and blocked results.
- Separate specification mismatches, authentication issues, authorization/ownership/tenant issues, API contract issues, corrected test defects, and environment blockers.
- State material user-task outcomes covered or still at risk when the endpoints support a user-facing flow.
- Risk-prioritized remaining endpoint, access-state, validation, CRUD, and edge-case work.

Distinguish tests implemented, executed, and passed. Never claim execution or coverage from generated source alone, and do not clutter the report with unrelated or temporary files.
