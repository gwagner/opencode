---
name: todo-capture
description: Captures detailed deferred work in /code/todo.md, or unresolved work in /code/blocked-todos.md, during normal non-loop work.
---

# Todo Capture

Use this skill when normal non-loop work reveals an actionable task that should be saved for later execution.

If the active prompt contains `TODO_LOOP_MODE=true`, do not use this skill. Use `todo-upkeep` instead.

## Target files

- Append implementation-ready work to `/code/todo.md`.
- Append work blocked by an unanswered execution-critical decision to `/code/blocked-todos.md`.
- Create either file when needed.

## Authoritative updates

Before capture, determine whether the work requires a requirements or specification creation, correction, or clarification. Delegate authoritative requirement updates to `prd-strategist` and specification updates to `code-spec-engineer`. Complete those updates before writing either a normal or blocked todo. Do not substitute todo metadata for required authoritative documentation.

## Format

Use one top-level unchecked checkbox for one independently executable and reviewable outcome. Split separately executable outcomes into separate todos instead of hiding them in one summary task.

Every implementation-ready entry must include exactly one nonempty `Branch:` plus `Scope:`, `Why:`, `Actions:`, `Evidence:`, and `Acceptance:`. Derive a deterministic, Git-valid branch name from the task outcome (for example, `fix/checkout-validation`); never reuse a branch for unrelated work. If a child todo cannot start until its parent todo completes, add exactly one nonempty `Depends on:` value to the child containing the parent's exact `Branch:` value. Never add child references to the parent. The dependency must be Git-valid and must not reference the current todo. Omit `Depends on:` when there is no parent dependency. Acceptance must state observable outcomes and relevant validation. Use path:line evidence when available; otherwise identify the authoritative source or state why direct evidence is not yet available. Blocked entries omit `Branch:` until promoted.

```markdown
- [ ] Prevent invalid checkout submission
  - Branch: fix/checkout-validation
  - Depends on: feat/checkout-contract
  - Scope: `src/checkout.ts` validation flow and related tests.
  - Why: Invalid data currently reaches the save API.
  - Actions:
    - Correct the validation control flow.
    - Add regression coverage for rejected submissions.
  - Evidence: `src/checkout.ts:42` returns success after validation failure.
  - Acceptance: Invalid submission displays an error, does not call the save API, and relevant tests pass.
  - Handoff: bug-fixer
```

Use `/code/blocked-todos.md` when an execution blocker remains:

```markdown
- [ ] Define webhook retry policy
  - Scope: `src/webhooks/dispatch.ts` and the webhook delivery contract.
  - Why: Failure behavior must be defined before retry logic can be implemented.
  - Actions:
    - Decide the retry limit and backoff schedule.
    - Record the approved policy in requirements and specifications.
  - Evidence: `src/webhooks/dispatch.ts:88` retries without a limit.
  - Acceptance: Approved sources define retry limit, backoff, terminal failure, and required tests.
  - Blocked by: Product decision on retry limit and backoff.
  - Required to unblock:
    - Approve the retry limit and backoff schedule.
    - Record the approved policy in requirements and specifications.
  - Questions: What retry limit and backoff schedule apply?
```

Use only these metadata labels: `Branch:`, `Depends on:`, `Scope:`, `Why:`, `Actions:`, `Evidence:`, `Acceptance:`, `Assumptions:`, `Blocked by:`, `Required to unblock:`, `Questions:`, `Handoff:`.

`Handoff:` is allowed only for implementation-ready work. Allowed values are exactly `bug-fixer` and `code-implementor`.
Every blocked entry must state both the obstacle in `Blocked by:` and the actions, decisions, information, or authoritative updates needed in `Required to unblock:`.

## Rules

1. Capture only concrete, actionable work.
2. Do not duplicate an equivalent unchecked entry in the target file.
3. Do not perform captured work unless explicitly asked.
4. Preserve existing checked/unchecked state and ordering.
5. Keep titles concise, but never omit actions or required execution context to shorten an entry.
6. Record material assumptions explicitly.
7. If an execution blocker remains, create a blocked entry instead of omitting the work or creating a routed todo.
8. Route a reported or reproducible defect to `bug-fixer`; route every other executable change to `code-implementor`.

## Before finishing

Report each target file and every added or deduplicated entry.
