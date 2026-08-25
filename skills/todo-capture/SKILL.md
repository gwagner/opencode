---
name: todo-capture
description: Captures deferred work in /code/todo.md as loop-compatible todo blocks during normal non-loop coding when the active prompt does not contain TODO_LOOP_MODE=true.
---

# Todo Capture

Use this skill when normal non-loop work reveals an actionable task that should be saved in `/code/todo.md` but is outside the current focused change.

If the active prompt contains `TODO_LOOP_MODE=true`, do not use this skill. For follow-up tasks discovered while executing a loop-runner task, use `todo-upkeep` instead.

## When to use

- A bug is found but the user did not ask to fix it now.
- Validation exposes an unrelated failure that should be revisited.
- Code inspection reveals missing cleanup, documentation, tests, or follow-up work.
- The user asks to remember, track, queue, or add a todo.

## Target file

Always append to `/code/todo.md`. Create `/code/todo.md` if it does not exist.

## Format

Append todos as compact, readable, loop-compatible markdown blocks. The first line must be a top-level unchecked checkbox action:

```markdown
- [ ] Task description
```

Add indented metadata bullets when useful for independent execution. All metadata fields are optional, but include enough context to make the task actionable without re-discovery:

```markdown
- [ ] Fix bug: save button ignores validation errors
  - Scope: `src/checkout.ts` validation flow and related tests.
  - Why: Users can submit invalid checkout data.
  - Evidence: `src/checkout.ts:42` returns success after validation failure.
  - Acceptance: Invalid submission shows an error and does not call the save API.
  - Handoff: bug-fixer
```

Use only these metadata labels when adding context: `Scope:`, `Why:`, `Evidence:`, `Acceptance:`, `Handoff:`.

`Handoff:` is optional. Allowed values are exactly `bug-fixer` and `code-implementor`. Route a reported or reproducible defect needing diagnosis or a fix to `bug-fixer`; route every other implementation-ready change to `code-implementor`. Never use a handoff for clarification or document updates.

## Rules

1. Capture only concrete, actionable work.
2. Do not duplicate an equivalent unchecked todo already present.
3. Do not perform the captured todo unless the user explicitly asks.
4. Keep the current focused task unchanged.
5. Preserve existing checked/unchecked task state and ordering.
6. Keep metadata concise; prefer path:line evidence when available.
7. Before adding `Handoff:`, resolve every execution-blocking product, contract, scope, or acceptance question. If answers are unavailable in a non-interactive session, do not create a routed todo; report the blocker. Non-blocking questions must not delay capture.

## Before finishing

Report `/code/todo.md` and the todos added. If no todo was added because a duplicate existed, say so.
