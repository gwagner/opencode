---
name: postgres-schema-designer
description: Designs PostgreSQL schema specification documents. Use with specification work involving entities, constraints, keys, indexes, relationships, or transaction rules.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: postgres-schema-designer
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: postgres-schema-designer
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: postgres-schema-designer
inputs:
  - approved persistence requirements
  - permitted specification destination
---

# PostgreSQL schema design

Use after `data-persistence-modeling` has established that PostgreSQL persistence is relevant.

1. Read only the feature, workflow, API, and existing schema evidence relevant to the change.
2. Produce focused, linked table documents in the calling agent's permitted specification directory.
3. Define normalized entities, keys, constraints, indexes, relationships, tenancy, and transaction-aware lifecycle rules.
4. Do not invent product behavior. Label assumptions and unresolved persistence questions.

Keep schema documentation separate from executable migrations. Use `postgres-migration` only when an implementation task requires a forward-only migration.
