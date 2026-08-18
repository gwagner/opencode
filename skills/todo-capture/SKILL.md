---
name: todo-capture
description: Captures deferred work in /code/todo.md during normal non-loop coding when the active prompt does not contain TODO_LOOP_MODE=true.
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

Append todos as markdown checkboxes:

```markdown
- [ ] Task description
```

If the todo comes from a bug, include enough reproduction context:

```markdown
- [ ] Fix bug: <symptom>; observed while <command/action>; suspected area: <file/component>
```

## Rules

1. Capture only concrete, actionable work.
2. Do not duplicate an equivalent unchecked todo already present.
3. Do not perform the captured todo unless the user explicitly asks.
4. Keep the current focused task unchanged.
5. Preserve existing checked/unchecked task state and ordering.
6. Add at most one concise context line below a todo when needed:

```markdown
- [ ] Fix bug: save button ignores validation errors
  - Context: Found during checkout form validation; see `src/checkout.ts`.
```

## Before finishing

Report `/code/todo.md` and the todos added. If no todo was added because a duplicate existed, say so.
