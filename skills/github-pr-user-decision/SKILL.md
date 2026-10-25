---
name: github-pr-user-decision
description: Routes one exact checked pull-request head through explicit user approval or non-mutating rejection.
classification: technical
opencode_permission:
  question: allow
  shell:
    "python3 /code/skills/github-pr-check-validation/scripts/validate-checks.py *": allow
    "python3 /code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py *": allow
    "python3 /code/skills/github-pr-rejection/scripts/verify-rejection.py *": allow
  external_directory:
    "/code/skills/github-pr-check-validation/scripts/validate-checks.py": allow
    "/code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py": allow
    "/code/skills/github-pr-rejection/scripts/verify-rejection.py": allow
  skill:
    github-pr-approved-merge: allow
    github-pr-rejection: allow
    grillme: allow
inputs:
  - one open ready pull request with passed required-check evidence
  - exact pull-request head branch, head commit, and base branch
  - expected GitHub repository from the current checkout
  - user available to approve or reject that exact head branch and head commit
---

# GitHub pull-request user decision

## Inputs

Require one open ready pull request with passed required-check evidence, its exact head branch, head commit, and base branch, the expected GitHub repository from the current checkout, and a user available to approve or reject that exact branch and head.

## Workflow

```yaml
request: "One exact-branch-and-head pull request concluded as merged or rejected-open."
workflow:
  - id: decision
    when: "The open pull request has passed required checks at the expected head branch and head commit."
    ask: "Approve or reject this exact pull request, head branch, and head commit?"
  - id: outcome
    when: "The user answered for the exact pull request, unchanged head branch, and unchanged head commit in the current turn."
    repeat_until: "The user explicitly approves or rejects the exact pull request, head branch, and head commit."
    select:
      question: "Which exact-branch-and-head decision did the user make?"
      precedence: "Evaluate branches in listed order; the final branch is fallback."
      branches:
        - when: "The user explicitly approved squash merge of the exact head branch and head commit."
          skill: github-pr-approved-merge
        - when: "The user explicitly rejected the exact head branch and head commit."
          skill: github-pr-rejection
        - when: "otherwise"
          skill: grillme
```

Approval is invalid after any head commit, head branch, base, state, or required-check change. Rejection performs no mutation and leaves the PR and branch open. Ambiguous or absent answers remain `waiting-user-decision`; never infer approval or rejection.

## Completion

Report `merged` or `rejected-open-pr`; exact head branch, head commit, check evidence, user decision, and blocker. Remote branch cleanup follows a merged result in the owning orchestrator.
