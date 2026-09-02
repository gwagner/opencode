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

Before capture, determine whether authoritative documents need creation, correction, or clarification. Delegate product requirements to `prd-strategist`, shared architecture or cross-feature decisions to `app-spec-architect`, and bounded feature contracts to `code-spec-engineer`. Complete required updates before writing an implementation-ready todo. For blocked work, complete updates that are possible and list any decision-dependent authoritative update in `Required to unblock:`. Do not substitute todo metadata for authoritative documentation.

## Format

Load and apply `todo-entry-contract`; it is the canonical entry schema and routing policy.

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

## Rules

1. Capture only concrete, actionable work.
2. Do not duplicate an equivalent unchecked entry in the target file.
3. Do not perform captured work unless explicitly asked.
4. Preserve existing checked/unchecked state and ordering.
5. Keep titles concise, but never omit actions or required execution context to shorten an entry.
6. If an execution blocker remains, create a blocked entry instead of omitting the work or creating a routed todo.

## Before finishing

Report each target file and every added or deduplicated entry.
