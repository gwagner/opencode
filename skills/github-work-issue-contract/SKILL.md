---
name: github-work-issue-contract
description: Validates lifecycle-aware canonical GitHub work-issue contracts without publishing or changing authority.
classification: non-technical
opencode_permission:
  read: allow
inputs:
  - one atomic work item
  - lifecycle_context: new_candidate or existing_issue
  - caller-permitted paths to verified authority references
  - current GitHub repository
  - candidate or existing-issue lifecycle evidence
---

# GitHub work issue contract

## Inputs

Require one atomic work item, `lifecycle_context` equal to `new_candidate` or `existing_issue`, caller-permitted paths to verified authority references, the current GitHub repository, and lifecycle evidence for the candidate or existing issue. Read the supplied authority paths to validate the candidate; the caller remains the runtime path restrictor.

Use to validate a proposed new issue or an identified existing issue. The caller owns authority coordination, clarification, GitHub operations, and publication.

## Issue boundary

- Use one open GitHub issue for one independently executable and reviewable outcome.
- Split independently executable outcomes into separate issues.
- Limit `Actions` to three concrete implementation steps. Do not use umbrella actions such as “implement feature”, “complete workflow”, or “update all affected code”.
- Do not duplicate an equivalent open issue.
- Use the current checkout's GitHub repository. Never publish to a repository inferred from issue content.

## Authority prerequisite

For `new_candidate`, verified authority references must support every ready-schema field. Issue text, repository behavior, caller assertions, and assumptions are not authority. Authority is incomplete when product intent, shared or cross-feature architecture, or a bounded feature contract is missing; the manager classifies the owner. A requirements/specification conflict is `authority_conflict`. A non-blocking uncertainty is an explicit assumption; an execution-blocking ambiguity is `blocking_question`. Issue metadata never substitutes for authority.

## New-candidate ready result

For `lifecycle_context: new_candidate`, return `contract_status: validated_ready` only when authority is complete and consistent, there are no blocking questions, the scope is atomic, the route is known, and the complete ready schema is present. The result includes canonical title and ordered body, `status_label: openchamber:ready`, `execution_route: github-sdlc`, verified authority references, explicit assumptions, empty blocking questions, and a duplicate-comparison key. Otherwise reject with exactly one applicable category: `authority_missing`, `authority_conflict`, `blocking_question`, `non_atomic_scope`, `schema_incomplete`, `route_unknown`, or `new_blocked_forbidden`.

A valid new candidate has `openchamber:ready` as its only OpenChamber status label and must not have `openchamber:blocked`. Unrelated repository labels may remain. Its body uses these sections in order:

- `Scope` — bounded files, subsystem, or contract.
- `Why` — user or system impact.
- `Actions` — no more than three concrete implementation steps.
- `Evidence` — path-and-line evidence when available, otherwise an authoritative source or explicit evidence limitation.
- `Acceptance` — observable outcomes and relevant validation.
- `Execution route` — exactly `github-sdlc` for every ready issue. The route is the issue-originated lifecycle owner, not the implementation specialist.
- `Processing handoff` — a required prominent section that says: “Before investigating, planning, or implementing this issue, the initially active session agent MUST hand the request to `github-sdlc`. Any other agent MUST NOT process this issue directly.”
- `Delivery` — fixed instructions that a user manually starts an OpenChamber worktree from the issue, explicitly selects local `main` as the starting branch, and selects `github-sdlc`. That action authorizes `github-sdlc` to validate the worktree, select exactly one implementation specialist, review and commit validated delegate-owned changes, push, open a pull request, and wait for required checks. Before requesting merge approval or merging, `github-sdlc` must post and verify a pre-closure issue update that names the delivered outcome and validation results. When dependency closure identifies browser impact, the update must embed labelled Before and After screenshots from the same deterministic scenario using native `gh issue comment --attach` with accessible alt text; screenshots never substitute for `frontend-impact-validation`. When browser impact is absent, the update must state that visual evidence is not required. `github-sdlc` must obtain explicit user approval for the exact pull-request head before squash merge, then delete only the remote feature branch, post a verified completion comment, and close the issue. The user remains responsible for archiving or deleting the OpenChamber session and confirming local worktree removal.
- Optional `Depends on` — one or more GitHub issue references that must close before work starts.

The processing handoff is issue-body text only: it does not natively select, route, or dispatch an OpenChamber agent. A user manually starts a worktree from the issue and selects `github-sdlc`. OpenChamber owns the resulting branch name, so the issue must not prescribe a branch.

## Existing-issue blocked result

Only for `lifecycle_context: existing_issue`, a blocked issue may have `openchamber:blocked` as its only OpenChamber status label and must not have `openchamber:ready`. Unrelated repository labels may remain. Its body uses `Scope`, `Why`, `Actions`, `Evidence`, and `Acceptance`, followed by:

- `Blocked by` — the current execution-critical obstacle.
- `Required to unblock` — decisions, information, actions, dependency closures, or authoritative updates needed.
- Optional `Questions` and `Assumptions`.

Blocked issues do not use `Execution route`. Promote only after every execution blocker is resolved; then apply the complete ready schema before changing labels. Reject any `new_candidate` that selects or contains blocked status as `new_blocked_forbidden`.

## Completion

Return the lifecycle context and either the valid new-candidate result or one rejection category. For `validated_ready`, return the canonical title, ordered body, ready label, execution route, processing handoff, authority references, assumptions, empty blocking questions, and duplicate-comparison key. For `existing_issue`, return the applicable ready or blocked contract result.
