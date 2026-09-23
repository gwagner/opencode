---
name: data-persistence-modeling
description: Designs or reconstructs application entities, PostgreSQL schemas, relationships, constraints, indexing, transactions, tenancy, and audit history.
classification: non-technical
opencode_permission:
  read: allow
inputs:
  - persistence scope
  - caller-provided permitted authority schema source and test evidence paths
compatibility: opencode
metadata:
  domain: data-architecture
  preferred-database: postgresql
---

# Data and persistence modeling

## Inputs

Require persistence scope and caller-provided permitted authority, schema, source, and test evidence paths.

Use this skill to specify application data behavior.

## Entity specification

For each major entity define:

- Purpose
- Ownership
- Lifecycle
- Relationships
- API exposure
- Sensitive-data considerations
- Audit requirements

Use a schema table:

| Field | Type | Required | Default | Constraints | Relationships | Meaning | Source |
|---|---|---|---|---|---|---|---|

## PostgreSQL design

When designing, prefer PostgreSQL-friendly constructs:

- Explicit primary and foreign keys
- Appropriate uniqueness constraints
- Check constraints for invariant enforcement
- Partial or composite indexes based on access patterns
- `timestamptz` for event times
- Transactional state changes
- Separate history or audit records when lifecycle reconstruction matters
- Explicit tenant keys where multi-tenant
- Idempotency keys or event records for external ingestion
- Persisted unique tie-breakers for every ordered collection

For each concurrency-sensitive invariant, map the invariant to both the application transition guard and the strongest appropriate database constraint, exclusion rule, conditional update, lock, or unique key. Name the transaction owner, race behavior, and failure result; application checks alone do not prove race safety.

For every paginated, timeline, history, queue, or latest query, define one total persisted order: authoritative business timestamp or state first, followed by a unique persisted identifier. Apply the complete order before slicing and reuse it across refresh, retry, cursor, and page traversal.

## Reverse-engineering reconciliation

Compare:

- Migrations
- Current schema
- Go models
- Repository queries
- API DTOs
- Frontend types
- Fixtures and tests

Persisted constraints are stronger evidence than unvalidated application types.

When persistence access is specified, describe application operations and transaction ownership. Do not require repository contracts to expose ORM, query-builder, or database-driver types.

## Required considerations

Document:

- Nullability
- Defaults
- Enumerated states
- Uniqueness
- Referential actions
- Indexes
- Soft deletion
- Retention
- Tenant isolation
- Optimistic or pessimistic concurrency
- Transaction boundaries
- Service and database enforcement for concurrency-sensitive invariants
- Complete `ORDER BY` and page-boundary behavior for ordered reads
- Raw webhook or transcript retention
- Personally identifiable or sensitive information
