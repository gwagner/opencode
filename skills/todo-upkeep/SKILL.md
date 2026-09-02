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

Before capture, determine whether authoritative documents need creation, correction, or clarification. Delegate product requirements to `prd-strategist`, shared architecture or cross-feature decisions to `app-spec-architect`, and bounded feature contracts to `code-spec-engineer`. Complete required updates before writing an implementation-ready todo. For blocked work, complete updates that are possible and list any decision-dependent authoritative update in `Required to unblock:`. Do not substitute todo metadata for authoritative documentation.

## Rules

1. Add only concrete work necessary to finish the current objective or safely handle a newly discovered follow-up.
2. Do not add speculative, duplicate, or unrelated work.
3. Load and apply `todo-entry-contract`; it is the canonical entry schema and routing policy.
4. If an execution-critical question remains unanswered, add a detailed entry to `/code/blocked-todos.md`; do not add a routed todo.
5. Keep titles concise, but never omit actions or required execution context to shorten an entry.
6. Do not mark the active task complete unless the loop prompt or user explicitly instructs it.
7. Preserve existing task order and checked/unchecked state.

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
