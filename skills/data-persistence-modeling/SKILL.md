---
name: data-persistence-modeling
description: Designs or reconstructs application entities, PostgreSQL schemas, relationships, constraints, indexing, transactions, tenancy, and audit history.
compatibility: opencode
metadata:
  domain: data-architecture
  preferred-database: postgresql
---

# Data and persistence modeling

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
- Raw webhook or transcript retention
- Personally identifiable or sensitive information
