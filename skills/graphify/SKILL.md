---
name: graphify
description: Investigates a codebase efficiently with graphify. Use when answering codebase questions, tracing code relationships, or updating an existing knowledge graph after code changes.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: api-integration-tester
      source: /code/agents/api-integration-tester.md
      allowed_skill: graphify
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: graphify
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: graphify
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: graphify
    - agent: spec-gap-detector
      source: /code/agents/spec-gap-detector.md
      allowed_skill: graphify
    - agent: todo-planner
      source: /code/agents/todo-planner.md
      allowed_skill: graphify
inputs:
  - codebase question or changed code
  - existing graph output
---

# Graphify

The root directory of any graphify operation is always in `/code/`

Use only when `/code/graphify-out/graph.json` exists. Otherwise, use normal repository inspection; do not create or repair graph output unless requested.

1. Start codebase investigation with `graphify query "<question>"`.
    - If you are looking for callers of your query, add `--context call --dfs`
    - If you are looking to follow a data relationship, add `--context field`
2. Use `graphify explain "<concept>"` for one focused concept and `graphify path "<A>" "<B>"` for a relationship.
   - Choose `query` for an unknown area, `explain` for a known concept, and `path` only after identifying both endpoints from Graphify output.
   - Use `--context call --dfs` for callers or dependencies, or `--context field` for data relationships. Do not combine them unless both are needed.
3. For broad navigation, read `graphify-out/wiki/index.md` when it exists. Read `GRAPH_REPORT.md` only for broad architecture review or when focused results are insufficient.
4. Use raw file search only to verify, fill a graph gap, or when graphify is unavailable.
5. After relevant code changes, run `graphify update .`. Dirty graph output alone is not a reason to skip it.
