---
name: github-pr-approved-merge
description: Squash-merges one user-approved GitHub pull request after canonical required-check validation of its unchanged head.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-check-validation/scripts/validate-checks.py *": allow
    "python3 /code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py *": allow
  external_directory:
    "/code/skills/github-pr-check-validation/scripts/validate-checks.py": allow
    "/code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py": allow
  skill:
    github-pr-check-validation: allow
inputs:
  - one open GitHub pull request targeting main
  - explicit user merge approval for the exact pull request, head branch, and head commit
  - expected GitHub repository from the current checkout
  - authenticated GitHub CLI
---

# GitHub approved pull-request merge

## Inputs

Require one open GitHub pull request targeting `main`, explicit user merge approval naming the exact pull request, head branch, and head commit, the expected GitHub repository from the current checkout, and an authenticated GitHub CLI.

## Workflow

```yaml
request: "One squash-merged, user-approved pull request."
workflow:
  - id: required-check-recheck
    when: "The open pull request, approved head branch, head commit, and base branch have passed the initial merge gate."
    skill: github-pr-check-validation
```

## Procedure

1. Require open state, base `main`, mergeable status, ready state, and an exact match between the current head branch, head commit, and current-turn user approval.
2. Invoke `github-pr-check-validation` immediately before merging, supplying this exact current head. Require its `passed` result.
3. Run `python3 /code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py --pr <pr> --expected-head <approved head> --expected-branch <approved branch> --expected-base main`.
4. Require one versioned JSON result. Accept `merged` only after the squash command succeeds and the script verifies checkout-repository identity, merged state, and unchanged head, head branch, and base. Treat a merged state after a failed squash command as an unowned external merge and return `blocked-unsafe`.

## Boundaries

- Never parse, classify, or recheck required checks outside `github-pr-check-validation`; never bypass its result, use administrative merge, infer approval, merge a changed head, or merge into a base other than `main`.
- Never delete a local or remote branch, worktree, or directory. Remote branch cleanup belongs to `github-pr-remote-branch-cleanup`.

## Completion

Report `merged`, `waiting-external`, or `blocked-unsafe`; repository, pull-request URL, approved head and base branch, canonical required-check result, squash-merge result, and blocker.
