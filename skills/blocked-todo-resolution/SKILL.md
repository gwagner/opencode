---
name: blocked-todo-resolution
description: Resolves self-contained entries in /code/blocked-todos.md through grillme and authoritative document updates, then promotes executable work to /code/todo.md without requiring code access.
---

# Blocked Todo Resolution

Use this skill when the user asks to resolve, review, or promote work from `/code/blocked-todos.md`.

## Procedure

1. Read `/code/blocked-todos.md` and select the requested entry. Treat its scope, actions, evidence, acceptance criteria, `Blocked by:`, `Required to unblock:`, questions, and assumptions as the complete starting context.
2. Do not require a code checkout, restore code, inspect code, or independently research existing requirements or specifications. If the entry lacks information needed for resolution, address that gap through clarification rather than repository investigation. Do not start implementation.
3. Load `grillme` and run a focused clarification session for every unresolved execution-blocking question. Ask questions sequentially and do not revisit answers already established by the blocked entry or the user.
4. Classify each answer by ownership:
   - Product intent, business rules, user-visible behavior, scope, or acceptance -> delegate to `prd-strategist`.
   - Implementation contract, API, data, workflow, security, or technical behavior -> delegate to `code-spec-engineer`.
   - Delegate to both when both authoritative layers require updates.
5. Require each specialist to update its authoritative documents and report changed paths, path:line evidence, decisions, assumptions, and remaining questions. Specialists must not edit production code or todo files.
6. Compare specialist reports with the blocked entry and clarification answers. Re-read only the documents changed by specialists when needed to verify that the reported updates captured those inputs.
7. If any execution blocker remains, update its `Blocked by:` and `Required to unblock:` metadata with the current obstacle, remaining resolution requirements, new evidence, answers, remaining questions, and document links. Do not promote it.
8. If all execution blockers are resolved, create one or more atomic, independently executable todos in `/code/todo.md`. Split separately executable outcomes.
9. Every promoted todo must include exactly one nonempty `Branch:` plus `Scope:`, `Why:`, `Actions:`, `Evidence:`, `Acceptance:`, and `Handoff:`. Derive a deterministic Git-valid branch name from the task outcome. Acceptance must include observable outcomes and relevant validation. Record material assumptions. Entries remaining blocked do not receive `Branch:`.
10. Route a reported or reproducible defect to `bug-fixer`; route every other implementation-ready change to `code-implementor`.
11. Remove the promoted entry from `/code/blocked-todos.md` only after all resulting todos have been written successfully to `/code/todo.md`.

## Rules

- Never implement promoted work.
- Never promote work with an unanswered execution-blocking question.
- Never edit authoritative requirements or specifications directly; use their owning specialists.
- Preserve the entry's existing evidence and traceability from the promoted todo to recorded answers and updated authoritative sources. Do not require new code evidence.
- Resolution must remain possible without restoring or accessing application code; the blocked entry is the sole prerequisite input.
- Keep `Handoff:` exclusive to implementation-ready routing. Blocked entries use `Blocked by:` and `Required to unblock:` instead.
- Deduplicate against existing unchecked todos before promotion.

## Final response

State which blocked entry was resolved or remains blocked, authoritative documents updated, answers recorded, and todos promoted or deduplicated.
