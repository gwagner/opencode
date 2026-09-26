---
name: github-work-issue-contract
description: Defines the canonical schema, authority prerequisite, routing, dependency, and blocked-state rules for GitHub work issues.
classification: non-technical
opencode_permission:
  task:
    prd-strategist: allow
    app-spec-architect: allow
    code-spec-engineer: allow
inputs:
  - one atomic work item
  - authority status
  - current GitHub repository
  - ready or blocked status
---

# GitHub work issue contract

## Inputs

Require one atomic work item, its authority status, the current GitHub repository, and a ready or blocked status.

## Deterministic workflow

```yaml
request: "Canonical authority-ready GitHub work issue"
workflow:
  - id: "select-authority-owner"
    when: "Authoritative documents require updates before issue publication or promotion."
    select:
      question: "Which authority owner must update the missing source?"
      precedence: "Evaluate branches in listed order; the final branch is fallback."
      branches:
        - when: "Product intent requires an update."
          agent: "prd-strategist"
        - when: "Shared architecture or a cross-feature decision requires an update."
          agent: "app-spec-architect"
        - when: "otherwise"
          agent: "code-spec-engineer"
```

Use whenever creating, updating, validating, or promoting a GitHub work issue.

## Issue boundary

- Use one open GitHub issue for one independently executable and reviewable outcome.
- Split independently executable outcomes into separate issues.
- Limit `Actions` to three concrete implementation steps. Do not use umbrella actions such as “implement feature”, “complete workflow”, or “update all affected code”.
- Do not duplicate an equivalent open issue.
- Use the current checkout's GitHub repository. Never publish to a repository inferred from issue content.

## Authority prerequisite

Before publishing or promoting a ready issue, determine whether authoritative documents need updates. Route product intent to `prd-strategist`, shared architecture or cross-feature decisions to `app-spec-architect`, and bounded feature contracts to `code-spec-engineer`. Each owner updates its authority and reports paths, evidence, decisions, assumptions, and remaining questions. Complete required updates before ready work. A blocked issue may record decision-dependent authority updates under `Required to unblock`; issue metadata never substitutes for authority.

## Ready issues

A ready issue has `openchamber:ready` as its only OpenChamber status label and must not have `openchamber:blocked`. Unrelated repository labels may remain. Its body uses these sections in order:

- `Scope` — bounded files, subsystem, or contract.
- `Why` — user or system impact.
- `Actions` — no more than three concrete implementation steps.
- `Evidence` — path-and-line evidence when available, otherwise an authoritative source or explicit evidence limitation.
- `Acceptance` — observable outcomes and relevant validation.
- `Execution route` — exactly `github-sdlc` for every ready issue. The route is the issue-originated lifecycle owner, not the implementation specialist.
- `Processing handoff` — a required prominent section that says: “Before investigating, planning, or implementing this issue, the initially active session agent MUST hand the request to `github-sdlc`. Any other agent MUST NOT process this issue directly.”
- `Delivery` — fixed instructions that a user manually starts an OpenChamber worktree from the issue, explicitly selects local `main` as the starting branch, and selects `github-sdlc`. That action authorizes `github-sdlc` to validate the worktree, select exactly one implementation specialist, review and commit validated delegate-owned changes, push, open a pull request, and wait for required checks. `github-sdlc` must obtain explicit user approval for the exact pull-request head before squash merge, then delete only the remote feature branch, post a verified completion comment, and close the issue. The user remains responsible for archiving or deleting the OpenChamber session and confirming local worktree removal.
- Optional `Depends on` — one or more GitHub issue references that must close before work starts.

The processing handoff is issue-body text only: it does not natively select, route, or dispatch an OpenChamber agent. A user manually starts a worktree from the issue and selects `github-sdlc`. OpenChamber owns the resulting branch name, so the issue must not prescribe a branch.

## Blocked issues

A blocked issue has `openchamber:blocked` as its only OpenChamber status label and must not have `openchamber:ready`. Unrelated repository labels may remain. Its body uses `Scope`, `Why`, `Actions`, `Evidence`, and `Acceptance`, followed by:

- `Blocked by` — the current execution-critical obstacle.
- `Required to unblock` — decisions, information, actions, dependency closures, or authoritative updates needed.
- Optional `Questions` and `Assumptions`.

Blocked issues do not use `Execution route`. Promote only after every execution blocker is resolved; then apply the complete ready schema before changing labels.

## Completion

Return the canonical title, ordered body, status label, execution route and processing handoff when ready, authority evidence, and duplicate-comparison key.
