---
name: api-integration-modeling
description: Designs or recovers HTTP APIs, handlers, contracts, authentication, errors, external integrations, webhooks, retries, and idempotency.
compatibility: opencode
metadata:
  domain: interface-architecture
---

# API and integration modeling

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
- Status codes
- Domain and persistence effects
- Side effects
- Error mapping
- Idempotency and concurrency behavior

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

## External integrations

For each integration define:

| System | Purpose | Direction | Authentication | Data exchanged | Trigger | Failure handling | Retry | Idempotency | Configuration | Source |
|---|---|---|---|---|---|---|---|---|---|---|

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
