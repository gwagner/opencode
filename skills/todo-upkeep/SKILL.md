---
name: todo-upkeep
description: Maintains /code/todo.md only when the active prompt contains TODO_LOOP_MODE=true and a looped task discovers required follow-up work for later loop iterations.
---

# Todo Upkeep

Use this skill only when the active prompt contains `TODO_LOOP_MODE=true`. That marker means the agent is executing one task from `/code/todo.md` through the loop runner.

This skill preserves newly discovered required follow-up work for later loop iterations.

If the active prompt does not contain `TODO_LOOP_MODE=true`, do not use this skill. For todos discovered during normal, non-loop coding or deferred bug triage, use `todo-capture` instead.

## Target file

Always append to `/code/todo.md`. Create `/code/todo.md` if it does not exist.

## Rules

1. Add only concrete, actionable tasks that are necessary to finish the current objective or safely handle newly discovered follow-up work.
2. Do not add speculative, nice-to-have, duplicate, or unrelated tasks.
3. Append new tasks as unchecked markdown checkboxes in `/code/todo.md`:
   - `- [ ] Task description`
4. Keep task text short but specific enough for a later loop iteration to execute independently.
5. If a task is blocked, add the unblock action rather than vague blocked status.
6. Do not mark the active task complete yourself unless explicitly instructed by the loop prompt or user.
7. Preserve existing task order and existing checked/unchecked status.

## Placement

- Append new tasks after the existing list unless the file already has a clearly labeled backlog/follow-up section.
- If adding multiple tasks, group them under:

```markdown
## Follow-up tasks

- [ ] First discovered task
- [ ] Second discovered task
```

## Task wording

Prefer:

- `- [ ] Add regression test for invalid API token response`
- `- [ ] Update README with loop runner todo-mode usage`
- `- [ ] Investigate missing Tailwind build script before frontend validation`

Avoid:

- `- [ ] Fix stuff`
- `- [ ] Maybe improve tests`
- `- [ ] Continue`

## Before finishing

When you add todos, mention the added task count and `/code/todo.md` in your final response.
