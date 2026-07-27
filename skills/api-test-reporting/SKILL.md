---
name: api-test-reporting
description: Summarize API integration-test coverage, execution results, contract mismatches, access-control findings, blockers, and remaining work.
compatibility: opencode
metadata:
    domain: api-testing
    phase: reporting
---

# API Integration Test Reporting

Use this skill after API discovery or integration-test execution.

Produce a concise report that makes coverage gaps and real API defects easy to distinguish from test or environment problems.

# API discovery

Report:

* specification sources inspected
* implementation/framework
* authentication mechanism
* authorization mechanism
* integration-test framework

# Coverage

Include:

* endpoints discovered
* endpoints covered
* public endpoints covered
* authenticated endpoints covered
* authorization-protected endpoints covered

When practical, use an endpoint matrix:

| Method | Endpoint | Auth | Test status |
| ------ | -------- | ---- | ----------- |

Useful test statuses include:

* covered
* partial
* failing
* blocked
* not started

# Files

List significant integration-test files:

* created
* modified
* supporting fixtures/helpers added

Do not clutter the report with unrelated generated or temporary files.

# Execution

Report the exact command used to run tests.

Include:

* passing
* failing
* skipped
* blocked

Do not describe tests as passing unless they were actually executed successfully.

# Findings

Separate findings into clear categories.

## Specification mismatches

For each mismatch state:

* endpoint
* specification behavior
* implementation behavior
* test impact

## Authentication issues

Report unexpected authentication behavior.

## Authorization issues

Report unexpected role, scope, ownership, or tenant behavior.

## API contract issues

Report:

* incorrect statuses
* incorrect response schemas
* undocumented behavior
* validation discrepancies

## Test defects

Mention test defects that were found and fixed when useful.

Do not confuse resolved test bugs with application defects.

## Environment blockers

Report missing:

* credentials
* databases
* dependencies
* configuration
* services
* runtime requirements

# Remaining work

Identify uncovered:

* endpoints
* authentication states
* authorization cases
* validation scenarios
* CRUD operations
* edge cases

Prioritize remaining work by API risk rather than simply listing everything.

# Accuracy

Never claim coverage based only on generated source files.

Differentiate:

* test implemented
* test executed
* test passed

These are separate states.

