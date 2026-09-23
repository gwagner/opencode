---
name: postgres-schema-designer
description: Designs PostgreSQL schema specification documents. Use with specification work involving entities, constraints, keys, indexes, relationships, or transaction rules.
classification: non-technical
opencode_permission:
  read: allow
  edit: allow
inputs:
  - approved persistence requirements
  - caller-provided permitted authority and schema evidence paths
  - permitted specification destination
---

# PostgreSQL schema design

## Inputs

Require approved persistence requirements, caller-provided permitted authority and schema evidence paths, and a permitted specification destination.

Use after `data-persistence-modeling` has established that PostgreSQL persistence is relevant.

1. Read only the feature, workflow, API, and existing schema evidence relevant to the change.
2. Produce focused, linked table documents in the calling agent's permitted specification directory.
3. Define normalized entities, keys, constraints, indexes, relationships, tenancy, and transaction-aware lifecycle rules.
4. For each concurrency-sensitive invariant, name its application transition guard, PostgreSQL constraint or guarded update, transaction owner, race behavior, and failure result.
5. For each paginated, timeline, history, queue, or latest query, specify a complete persisted `ORDER BY` ending in a unique persisted tie-breaker and define equal-key page-boundary behavior.
6. Do not invent product behavior. Label assumptions and unresolved persistence questions.

Keep schema documentation separate from executable migrations. Report an implementation handoff when a forward-only migration is required; the implementation caller owns its separately wired `postgres-migration` stage.
