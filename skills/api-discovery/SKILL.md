---
name: api-discovery
description: Discover API contracts, implemented routes, authentication requirements, and test infrastructure by comparing API specifications with application source code.
compatibility: opencode
metadata:
    domain: api-testing
    phase: discovery
---

# API Discovery

Use this skill before creating API integration tests.

The goal is to build an accurate inventory of the intended API contract and the actual implemented API surface.

## Inputs

The calling agent should identify:

* the location containing specifications or requirements
* the location containing application source code

Do not assume fixed paths unless the calling agent provides them.

# Discover the specification

Inspect the specification source recursively.

Look especially for:

* `openapi.yaml`
* `openapi.yml`
* `openapi.json`
* Swagger definitions
* API documentation
* endpoint specifications
* architecture documents
* requirements
* acceptance criteria
* authentication documentation
* API examples

Treat documented specifications as the intended contract.

# Discover the implementation

Inspect the application source recursively.

Determine:

* programming language
* web framework
* dependency/build system
* application startup method
* route definitions
* controllers and handlers
* middleware
* authentication implementation
* authorization implementation
* request and response models
* environment-variable requirements
* databases and dependent services
* existing integration tests
* existing fixtures, factories, clients, and test helpers

Treat the implementation as evidence of current application behavior, not automatically as the intended contract.

# Build an endpoint inventory

For every endpoint discovered, identify when possible:

* HTTP method
* route
* description
* specification source
* implementation source
* authentication requirement
* authorization requirement
* path parameters
* query parameters
* required headers
* request body
* expected success status
* documented error statuses
* response schema
* roles, permissions, or scopes

Classify each endpoint as one of:

* `PUBLIC`
* `AUTHENTICATED`
* `AUTHORIZED`

Use `UNKNOWN` when the available evidence is insufficient.

Do not silently guess authentication requirements.

# Compare specification and implementation

Map specification endpoints to implementation routes.

Identify discrepancies such as:

* endpoint documented but not implemented
* endpoint implemented but not documented
* different route
* different HTTP method
* different request fields
* different response fields
* different HTTP status
* different authentication requirement
* different authorization requirement

Do not automatically resolve discrepancies in favor of the implementation.

The specification describes intended behavior.

The implementation describes observed behavior.

Preserve both when they disagree.

# Discover test infrastructure

Before recommending a test implementation, determine whether the codebase already uses:

* an integration-test framework
* an HTTP/API client library
* test containers
* database fixtures
* mock servers
* authentication fixtures
* application test harnesses

Prefer existing project conventions.

Do not introduce a new framework when an appropriate one already exists.

# Output

Return a concise discovery result containing:

## Application

* language
* framework
* build system
* test framework
* startup mechanism

## Authentication

* authentication mechanisms
* credential acquisition mechanism
* authorization mechanisms

## Endpoint inventory

For each endpoint:

`METHOD PATH | classification | expected success | implementation status`

Include roles or scopes when relevant.

## Specification mismatches

Explicitly identify specification/implementation discrepancies.

## Testing infrastructure

Identify reusable test helpers, fixtures, clients, and conventions.

The result should give another agent enough information to start writing integration tests without rediscovering the API.

