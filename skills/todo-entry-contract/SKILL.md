---
name: todo-entry-contract
description: Defines the canonical schema, routing, dependencies, and blocked-state rules for entries in /code/todo.md and /code/blocked-todos.md.
---

# Todo entry contract

Use whenever creating, updating, validating, or promoting todo entries.

## Entry boundary

- Use one top-level unchecked checkbox for one independently executable and reviewable outcome.
- Split independently executable outcomes into separate entries.
- Default to smaller entries. An implementation-ready entry must fit one focused implementation pass and produce one independently testable user or system outcome.
- Split an entry when it changes more than one independently testable behavior, route or component boundary, or architectural layer. Create ordered child entries with `Depends on:` when work must be sequential.
- Limit `Actions:` to three concrete implementation steps. Do not use umbrella actions such as “implement feature”, “complete workflow”, or “update all affected code”.
- Preserve existing order and checked state; do not duplicate an equivalent unchecked entry.

## Authority prerequisite

Before an implementation-ready entry or promotion, determine whether authoritative documents need updates. Route product intent to `prd-strategist`, shared architecture or cross-feature decisions to `app-spec-architect`, and bounded feature contracts to `code-spec-engineer`. Each owner updates its authority and reports paths, evidence, decisions, assumptions, and remaining questions. Complete required updates before ready work; for unresolved work, record decision-dependent updates in `Required to unblock:`. Never substitute todo metadata for authority.

## Implementation-ready entries

Require exactly one nonempty value for each label:

- `Branch:` — deterministic, Git-valid local branch name unique to the outcome. The orchestrator creates or selects this branch before handing work to `Handoff:`; receiving agents work in the provided checkout and do not create or switch branches.
- `Scope:` — bounded files, subsystem, or contract.
- `Why:` — user or system impact.
- `Actions:` — concrete implementation steps.
- `Evidence:` — path:line evidence when available, otherwise an authoritative source or explicit evidence limitation.
- `Acceptance:` — observable outcomes and relevant validation.
- `Handoff:` — exactly `bug-fixer` for a reported or reproducible defect requiring diagnosis/fix; otherwise `code-implementor`.

Use optional `Assumptions:` only for material assumptions. Use optional `Depends on:` exactly once only when the entry cannot start until its parent completes; its value must equal the parent's Git-valid `Branch:` and must not reference itself. This is orchestrator dependency metadata, not a receiving-agent Git instruction. Parents never list children.

## Blocked entries

Blocked entries use `Scope:`, `Why:`, `Actions:`, `Evidence:`, and `Acceptance:` plus:

- `Blocked by:` — the current execution-critical obstacle.
- `Required to unblock:` — decisions, information, actions, or authoritative updates needed.
- Optional `Questions:` and `Assumptions:`.

Blocked entries never use `Branch:`, `Depends on:`, or `Handoff:`. Promote only after every execution blocker is resolved; then apply the complete implementation-ready schema before removing the blocked entry.

Use no metadata labels beyond those defined here.
