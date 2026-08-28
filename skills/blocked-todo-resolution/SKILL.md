---
name: blocked-todo-resolution
description: Resolves entries in /code/blocked-todos.md through grillme and authoritative document updates, then promotes executable work to /code/todo.md.
---

# Blocked Todo Resolution

Use this skill when the user asks to resolve, review, or promote work from `/code/blocked-todos.md`.

## Procedure

1. Read `/code/blocked-todos.md` and select the requested entry. Preserve its scope, actions, evidence, acceptance criteria, `Blocked by:`, `Required to unblock:`, questions, and assumptions as working context.
2. Read relevant requirements, specifications, and code evidence. Do not start implementation.
3. Load `grillme` and run a focused clarification session for every unresolved execution-blocking question. Ask questions sequentially and do not revisit answers already established by authoritative sources or the user.
4. Classify each answer by ownership:
   - Product intent, business rules, user-visible behavior, scope, or acceptance -> delegate to `prd-strategist`.
   - Implementation contract, API, data, workflow, security, or technical behavior -> delegate to `code-spec-engineer`.
   - Delegate to both when both authoritative layers require updates.
5. Require each specialist to update its authoritative documents and report changed paths, path:line evidence, decisions, assumptions, and remaining questions. Specialists must not edit production code or todo files.
6. Re-read the updated authoritative sources and compare them with the blocked entry and clarification answers.
7. If any execution blocker remains, update its `Blocked by:` and `Required to unblock:` metadata with the current obstacle, remaining resolution requirements, new evidence, answers, remaining questions, and document links. Do not promote it.
8. If all execution blockers are resolved, create one or more atomic, independently executable todos in `/code/todo.md`. Split separately executable outcomes.
9. Every promoted todo must include exactly one nonempty `Branch:` plus `Scope:`, `Why:`, `Actions:`, `Evidence:`, `Acceptance:`, and `Handoff:`. Derive a deterministic Git-valid branch name from the task outcome. Acceptance must include observable outcomes and relevant validation. Record material assumptions. Entries remaining blocked do not receive `Branch:`.
10. Route a reported or reproducible defect to `bug-fixer`; route every other implementation-ready change to `code-implementor`.
11. Remove the promoted entry from `/code/blocked-todos.md` only after all resulting todos have been written successfully to `/code/todo.md`.

## Rules

- Never implement promoted work.
- Never promote work with an unanswered execution-blocking question.
- Never edit authoritative requirements or specifications directly; use their owning specialists.
- Preserve traceability from the promoted todo to code evidence and updated authoritative sources.
- Keep `Handoff:` exclusive to implementation-ready routing. Blocked entries use `Blocked by:` and `Required to unblock:` instead.
- Deduplicate against existing unchecked todos before promotion.

## Final response

State which blocked entry was resolved or remains blocked, authoritative documents updated, answers recorded, and todos promoted or deduplicated.
