---
name: api-integration-testing
description: Build maintainable API integration tests using a project's existing framework, covering contracts, validation, CRUD flows, isolation, and safe execution.
compatibility: opencode
metadata:
    domain: api-testing
    phase: implementation
---

# API Integration Testing

Use this skill to implement executable API integration tests after API discovery has established the endpoint contract and authentication model.

# Follow project conventions

Before creating files, identify:

* existing test framework
* integration-test directory
* API client conventions
* fixture conventions
* test configuration
* formatting and linting requirements

Prefer the project's existing tools.

Do not introduce another test framework when a suitable one already exists.

# Test location

Use the project's existing integration-test location when present.

Common examples include:

* `tests/integration/`
* `test/integration/`
* `integration/`
* `e2e/`
* `src/test/`

If none exists, choose a conventional location appropriate for the project's language and framework.

# Baseline endpoint coverage

Create a useful baseline for every endpoint being covered.

Depending on endpoint type, test:

| Endpoint type | Required baseline                    |
| ------------- | ------------------------------------ |
| Public        | unauthenticated success              |
| Authenticated | unauthenticated rejection            |
| Authenticated | invalid-auth rejection               |
| Authenticated | authenticated success                |
| Authorized    | authenticated unauthorized rejection |
| Authorized    | authenticated authorized success     |

Use the API authentication skill for detailed authentication behavior.

# Contract assertions

Where appropriate, verify:

* HTTP status
* response content type
* required response fields
* field types
* documented response schema
* required headers
* documented error structure

Prefer stable contract assertions over volatile literal values.

Avoid asserting timestamps, generated identifiers, ordering, or dynamic values unless the contract guarantees them.

# Request validation

Add meaningful negative cases for:

* missing required fields
* malformed values
* invalid enum values
* invalid path parameters
* invalid query parameters
* unsupported content types
* nonexistent resources

Prioritize documented validation behavior.

Do not blindly generate combinatorial edge cases before baseline endpoint coverage exists.

# CRUD testing

For CRUD resources, prefer an isolated lifecycle:

1. create the test resource
2. capture its identifier
3. retrieve it
4. update it
5. verify the update
6. delete it
7. verify deletion or absence

Generate unique test data.

Do not depend on arbitrary preexisting records when the API allows tests to create their own.

# Isolation and repeatability

Integration tests should tolerate repeated execution.

Prefer:

* setup and teardown
* generated unique names or identifiers
* fixtures
* factories
* test-specific accounts
* temporary resources

Avoid relying on test execution order unless the framework explicitly supports an intentional ordered scenario.

# Configuration

Keep environment-dependent values configurable.

Examples:

* `API_BASE_URL`
* `TEST_USERNAME`
* `TEST_PASSWORD`
* `TEST_ACCESS_TOKEN`
* `TEST_API_KEY`

A harmless localhost default may be used when appropriate.

Do not embed environment-specific credentials.

# External dependencies

Determine whether integration tests require:

* database
* message broker
* cache
* identity provider
* container runtime
* external HTTP service

Reuse existing test infrastructure when available.

Do not silently redirect tests to production dependencies.

# Safe mutation

Assume API data may be important until a test environment is established.

Do not:

* truncate arbitrary databases
* drop schemas
* delete unrelated records
* run destructive migrations
* modify production configuration
* send destructive API calls to a production endpoint

When a safe test target cannot be established, create the relevant tests but skip destructive execution and report the blocker.

# Execute incrementally

After implementing a useful test slice:

1. format changed files
2. run the smallest relevant test set
3. fix test implementation defects
4. expand coverage
5. run the broader integration suite when appropriate

Do not modify application code solely to make the tests pass unless explicitly asked to fix the application.

# Failure classification

Classify failures before changing tests.

## TEST DEFECT

Examples:

* incorrect URL
* incorrect fixture
* authentication helper bug
* wrong assertion
* test framework misuse

Fix these.

## IMPLEMENTATION DEFECT

The implementation violates the intended API contract.

Preserve the meaningful failing test and report the defect.

## SPECIFICATION / IMPLEMENTATION MISMATCH

The implementation and specification disagree.

Report both behaviors.

Do not silently rewrite the test to mirror the implementation.

## ENVIRONMENT BLOCKER

Examples:

* database unavailable
* dependent service unavailable
* application cannot start
* missing credentials
* required container runtime unavailable

Preserve useful test code and report the blocker.

# Implementation quality

Keep integration-test code easy to extend.

Extract shared utilities when they eliminate meaningful repetition, especially:

* API client configuration
* authentication setup
* common request headers
* resource factories
* cleanup helpers

Avoid premature frameworks or elaborate internal DSLs.

Establish readable working tests first.

