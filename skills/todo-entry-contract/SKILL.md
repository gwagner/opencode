---
name: todo-entry-contract
description: Defines the canonical schema, routing, dependencies, and blocked-state rules for entries in /code/todo.md and /code/blocked-todos.md.
---

# Todo entry contract

Use whenever creating, updating, validating, or promoting todo entries.

## Entry boundary

- Use one top-level unchecked checkbox for one independently executable and reviewable outcome.
- Split independently executable outcomes into separate entries.
- Preserve existing order and checked state; do not duplicate an equivalent unchecked entry.

## Implementation-ready entries

Require exactly one nonempty value for each label:

- `Branch:` — deterministic, Git-valid local branch name unique to the outcome.
- `Scope:` — bounded files, subsystem, or contract.
- `Why:` — user or system impact.
- `Actions:` — concrete implementation steps.
- `Evidence:` — path:line evidence when available, otherwise an authoritative source or explicit evidence limitation.
- `Acceptance:` — observable outcomes and relevant validation.
- `Handoff:` — exactly `bug-fixer` for a reported or reproducible defect requiring diagnosis/fix; otherwise `code-implementor`.

Use optional `Assumptions:` only for material assumptions. Use optional `Depends on:` exactly once only when the entry cannot start until its parent completes; its value must equal the parent's Git-valid `Branch:` and must not reference itself. Parents never list children.

## Blocked entries

Blocked entries use `Scope:`, `Why:`, `Actions:`, `Evidence:`, and `Acceptance:` plus:

- `Blocked by:` — the current execution-critical obstacle.
- `Required to unblock:` — decisions, information, actions, or authoritative updates needed.
- Optional `Questions:` and `Assumptions:`.

Blocked entries never use `Branch:`, `Depends on:`, or `Handoff:`. Promote only after every execution blocker is resolved; then apply the complete implementation-ready schema before removing the blocked entry.

Use no metadata labels beyond those defined here.
