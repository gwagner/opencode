---
name: api-integration-modeling
description: Designs or recovers HTTP APIs, handlers, contracts, authentication, errors, external integrations, webhooks, retries, and idempotency.
classification: non-technical
opencode_permission:
  read: allow
inputs:
  - API or integration scope
  - caller-provided permitted authority and observed evidence paths
compatibility: opencode
metadata:
  domain: interface-architecture
---

# API and integration modeling

## Inputs

Require an API or integration scope and caller-provided permitted authority and observed evidence paths.

## Endpoint specification

Use this table:

| ID | Method | Path | Purpose | Authentication | Permission | Request | Response | Errors | Idempotency | Status | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|

For each important endpoint define:

- Path and method
- Authentication
- Authorization
- Path, query, and header parameters
- Request body
- Validation
- Response body
- Explicit transport/read-model field allowlist
- Status codes
- Domain and persistence effects
- Side effects
- Error mapping
- Idempotency and concurrency behavior
- Read-versus-command classification
- Null, unavailable, zero, empty, accepted, delivered, and failed semantics where relevant

Reads, refreshes, polling, streams, fragments, detail views, and diagnostics are observational unless authority explicitly defines a write. Specify any intentional read-side effect with its authority; otherwise require no provider call, send/replay, attempt allocation, session refresh, audit append, retention extension, retry/health mutation, or command-style row lock.

A frontend interaction-log ingestion endpoint is an explicit write-side diagnostic command, not an observational read. Define its same-origin path and method, authentication, authorization, request-protection mechanism, content type, schema version, event and field allowlists, maximum request bytes, batch count, field lengths, timestamp skew, rate limit, accepted and rejected semantics, retry guidance, duplicate-event behavior, and no-store response. The endpoint MUST accept no client-selected sink, severity, environment, tenant, identity, or unrestricted field map and MUST return no submitted content or internal logging detail.

## Backend structure

For Go applications, identify or design:

- Router and middleware
- Transport DTOs
- Handlers
- Services or use cases
- Domain models
- Repository interfaces
- PostgreSQL implementations
- Transaction ownership
- Background jobs
- Typed errors and transport mapping
- Context propagation
- Dependency construction

For an external, persistence, or cross-layer dependency, name the consumer-owned port when one is justified, its adapter, its failure and cancellation behavior, and the composition root. Do not expose transport, framework, ORM, or vendor types through the application-facing contract. Define explicit authorized configuration and credential provenance and list prohibited ambient fallback when authority requires persisted or caller-supplied configuration.

## External integrations

For each integration define:

| System | Purpose | Direction | Authentication | Data exchanged | Trigger | Failure handling | Retry | Idempotency | Configuration | Source |
|---|---|---|---|---|---|---|---|---|---|---|

For delayed or retried work, define the event-time snapshot creation point and immutable payload, destination, recipient, signing/configuration revision, and event identity. Later configuration edits must not alter queued work.

## Projection and error discipline

- Construct explicit transport or read-model allowlists; never serialize persistence entities implicitly.
- Redact provider, credential, secret-bearing, and internal errors before they enter transport, logs, metrics, audits, or diagnostics.
- Define stable machine error codes and safe status mappings.
- Preserve domain truth; do not convert absent or unavailable values into zero, success, empty, or fabricated values, and do not equate acceptance with delivery.

## Webhooks

Specify or verify:

1. Receipt
2. Signature verification
3. Payload validation
4. Event identity
5. Duplicate detection
6. Raw-payload persistence
7. Transactional processing
8. State updates
9. Side effects
10. Response semantics
11. Retry handling
12. Dead-letter or recovery process
13. Audit history

Do not claim idempotency without an explicit unique key, processed-event record, transaction guard, or demonstrated test.
