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

For `lifecycle_context: new_candidate`, return `contract_status: validated_ready` only when authority is complete and consistent, there are no blocking questions, the scope is atomic, the route is known, and the complete ready schema is present. The result includes canonical title and ordered body, `status_label: openchamber:ready`, `execution_route: sdlc-orchestrator`, verified authority references, explicit assumptions, empty blocking questions, and a duplicate-comparison key. Otherwise reject with exactly one applicable category: `authority_missing`, `authority_conflict`, `blocking_question`, `non_atomic_scope`, `schema_incomplete`, or `route_unknown`.

A valid new candidate has `openchamber:ready` as its only OpenChamber status label and must not have `openchamber:blocked`. Unrelated repository labels may remain. Its body uses these sections in order:

- `Scope` — bounded files, subsystem, or contract.
- `Why` — user or system impact.
- `Actions` — no more than three concrete implementation steps.
- `Evidence` — path-and-line evidence when available, otherwise an authoritative source or explicit evidence limitation.
- `Acceptance` — observable outcomes and relevant validation.
- `Execution route` — exactly `sdlc-orchestrator` for every ready issue. The route is the lifecycle owner, not the implementation specialist.
- `Processing handoff` — a required prominent section that says: “Before investigating, planning, or implementing this issue, the initially active session agent MUST hand the request to `sdlc-orchestrator` with entry point `github-issue`. Any other agent MUST NOT process this issue directly.”
- `Delivery` — fixed instructions that a user starts an OpenChamber worktree from the issue, selects local `main` only as the branch base, and selects `sdlc-orchestrator` with entry point `github-issue`. OpenChamber creates and checks out the non-`main` issue branch. The orchestrator validates or safely resumes that worktree, delegates sequential validated changes, publishes or recovers one pull request, and favors repair or resumable waiting over terminal failure. Required checks must pass before the user approves or rejects the exact pull-request head. Approval permits a rechecked squash merge, remote-branch cleanup, completion comment, and issue closure. Rejection performs no mutation and leaves the pull request, remote branch, and issue open. Browser evidence rules remain applicable and screenshots never replace `frontend-impact-validation`. The user remains responsible for OpenChamber session cleanup.
- Optional `Depends on` — one or more GitHub issue references that must close before work starts.

The processing handoff is issue-body text only: it does not natively select, route, or dispatch an OpenChamber agent. A user starts a worktree from the issue and selects `sdlc-orchestrator` with entry point `github-issue`. OpenChamber owns creation and checkout of the resulting non-`main` issue branch and its branch name, so the issue must not prescribe a branch and the orchestrator must not create one.

## Blocked result

For `lifecycle_context: new_candidate`, return `contract_status: validated_blocked` only when lifecycle policy explicitly sets `blocked_issue_creation: true`, the candidate has verified authority references, atomic scope, canonical title and body, a duplicate-comparison key, and an explicit execution-critical blocker. Otherwise return the applicable ready-result rejection category. A validated blocked result has `status_label: openchamber:blocked`, explicit blockers, and no `execution_route`, processing handoff, or delivery section.

For `lifecycle_context: existing_issue`, retain its applicable ready or blocked result. A blocked issue may have `openchamber:blocked` as its only OpenChamber status label and must not have `openchamber:ready`. Unrelated repository labels may remain. Its body uses `Scope`, `Why`, `Actions`, `Evidence`, and `Acceptance`, followed by:

- `Blocked by` — the current execution-critical obstacle.
- `Required to unblock` — decisions, information, actions, dependency closures, or authoritative updates needed.
- Optional `Questions` and `Assumptions`.

Blocked issues do not use `Execution route`, including policy-authorized validated blocked new candidates. Promote only after every execution blocker is resolved; then apply the complete ready schema before changing labels.

## Completion

Return the lifecycle context and either the valid new-candidate result or one rejection category. For `validated_ready`, return the canonical title, ordered body, ready label, execution route, processing handoff, authority references, assumptions, empty blocking questions, and duplicate-comparison key. For `validated_blocked`, return the canonical title, ordered body, blocked label, policy evidence, explicit blockers, authority references, and duplicate-comparison key, with no route. For `existing_issue`, return the applicable ready or blocked contract result.
