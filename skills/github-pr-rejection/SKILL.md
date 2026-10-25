---
name: github-pr-rejection
description: Verifies that one exact user-rejected pull request remains open and unchanged without mutating GitHub.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-rejection/scripts/verify-rejection.py *": allow
  external_directory:
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-pr-rejection/scripts/verify-rejection.py": allow
inputs:
  - exact pull request rejected by the user
  - exact rejected head branch, head commit, and base branch
  - expected GitHub repository from the current checkout
  - current-turn explicit rejection
  - authenticated GitHub CLI
---

# GitHub pull-request rejection

## Inputs

Require the exact pull request rejected by the user, its exact rejected head branch, head commit, and base branch, the expected GitHub repository from the current checkout, current-turn explicit rejection, and an authenticated GitHub CLI.

## Procedure

All lifecycle scripts import `/code/skills/github_pr_lifecycle_common.py` for fail-closed checkout identity, marker, remote-ref, JSON, and version-1 result-envelope primitives; this skill retains its operation-specific predicates and mutations.

1. Run `python3 /code/skills/github-pr-rejection/scripts/verify-rejection.py --pr <pr> --expected-head <head> --expected-branch <branch> --expected-base <base>`.
2. Require every configured `origin` fetch and effective push URL and the non-cross-repository pull-request head to match the checkout repository. Require `rejected-open-pr` with open state and unchanged head, head branch, and base branch.
3. Perform no GitHub or Git mutation. Leave the pull request, remote branch, and any originating issue open.

## Completion

Report `rejected-open-pr`, `waiting-external`, or `blocked-unsafe`; repository, PR URL, rejected head, branch, base, verification evidence, and blocker.
