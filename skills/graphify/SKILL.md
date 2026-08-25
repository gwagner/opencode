---
name: graphify
description: Investigates a codebase efficiently with graphify. Use when answering codebase questions, tracing code relationships, or updating an existing knowledge graph after code changes.
---

# Graphify

The root directory of any graphify operation is always in `/code/`

Use only when `/code/graphify-out/graph.json` exists. Otherwise, use normal repository inspection; do not create or repair graph output unless requested.

1. Start codebase investigation with `graphify query "<question>"`.
    - If you are looking for callers of your query, add `--context call --dfs`
    - If you are looking to follow a data relationship, add `--context field`
2. Use `graphify explain "<concept>"` for one focused concept and `graphify path "<A>" "<B>"` for a relationship.
3. For broad navigation, read `graphify-out/wiki/index.md` when it exists. Read `GRAPH_REPORT.md` only for broad architecture review or when focused results are insufficient.
4. Use raw file search only to verify, fill a graph gap, or when graphify is unavailable.
5. After relevant code changes, run `graphify update .`. Dirty graph output alone is not a reason to skip it.
