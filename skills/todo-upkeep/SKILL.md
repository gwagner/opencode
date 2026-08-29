---
name: todo-upkeep
description: Maintains detailed loop follow-ups in /code/todo.md and unresolved blockers in /code/blocked-todos.md when TODO_LOOP_MODE=true.
---

# Todo Upkeep

Use this skill only when the active prompt contains `TODO_LOOP_MODE=true`. Use `todo-capture` during normal non-loop work.

## Target files

- Append implementation-ready follow-up work to `/code/todo.md`.
- Append unresolved execution blockers to `/code/blocked-todos.md`.
- Create either file when needed.

## Authoritative updates

Before capture, determine whether the follow-up requires a requirements or specification creation, correction, or clarification. Delegate authoritative requirement updates to `prd-strategist` and specification updates to `code-spec-engineer`. Complete those updates before writing either a normal or blocked todo. Do not substitute todo metadata for required authoritative documentation.

## Rules

1. Add only concrete work necessary to finish the current objective or safely handle a newly discovered follow-up.
2. Do not add speculative, duplicate, or unrelated work.
3. Use one unchecked checkbox for one independently executable and reviewable outcome. Split separately executable outcomes into separate entries.
4. Every implementation-ready entry must include exactly one nonempty `Branch:` plus `Scope:`, `Why:`, `Actions:`, `Evidence:`, and `Acceptance:`. Derive a deterministic Git-valid name from the task outcome and do not reuse it for unrelated work. When a child follow-up requires its parent todo first, add exactly one nonempty `Depends on:` value to the child containing the parent's exact `Branch:` value. Never add child references to the parent. The dependency must be Git-valid and not self-referential. Omit the label when there is no parent dependency. Blocked entries omit `Branch:` until promoted.
5. Acceptance must state observable outcomes and relevant validation.
6. Use only these metadata labels: `Branch:`, `Depends on:`, `Scope:`, `Why:`, `Actions:`, `Evidence:`, `Acceptance:`, `Assumptions:`, `Blocked by:`, `Required to unblock:`, `Questions:`, `Handoff:`.
7. `Handoff:` is allowed only for implementation-ready work. Its value is exactly `bug-fixer` or `code-implementor`.
8. If an execution-critical question remains unanswered, add a detailed entry to `/code/blocked-todos.md`; do not add a routed todo.
9. Keep titles concise, but never omit actions or required execution context to shorten an entry.
10. Use path:line evidence when available; otherwise identify the authoritative source or state why direct evidence is unavailable.
11. Record material assumptions explicitly.
12. Do not mark the active task complete unless the loop prompt or user explicitly instructs it.
13. Preserve existing task order and checked/unchecked state.

## Blocked format

```markdown
- [ ] Define missing validation behavior
  - Scope: `src/api/create-user.ts` and its API contract.
  - Why: Validation rules are required before implementation can be completed.
  - Actions:
    - Decide whether the boundary is inclusive.
    - Update the authoritative contract after the decision.
  - Evidence: `src/api/create-user.ts:31` accepts an unspecified boundary value.
  - Acceptance: Approved sources define boundary behavior and required validation coverage.
  - Blocked by: Missing contract decision.
  - Required to unblock:
    - Decide whether the boundary is inclusive.
    - Update the authoritative contract.
  - Questions: Is the boundary inclusive or exclusive?
```

## Placement

Append new entries after the existing list unless the file has a clearly labeled backlog or follow-up section. Group multiple entries under `## Follow-up tasks` when appropriate.

## Before finishing

Report each target file and the number of entries added.
