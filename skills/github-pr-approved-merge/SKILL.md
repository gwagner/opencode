---
name: github-pr-approved-merge
description: Verifies that a user manually squash-merged one exact approved GitHub pull request without performing the merge.
classification: technical
opencode_permission:
  question: allow
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
  - explicit user approval for manual squash merge of the exact pull request, head branch, and head commit
  - user available to perform and confirm that manual squash merge
  - expected GitHub repository from the current checkout
  - authenticated GitHub CLI
---

# GitHub approved manual-merge verification

## Inputs

Require one open GitHub pull request targeting `main`, explicit user approval for manual squash merge of the exact pull request, head branch, and head commit, a user available to perform and confirm that manual squash merge, the expected GitHub repository from the current checkout, and an authenticated GitHub CLI.

## Workflow

```yaml
request: "One exact user-approved pull request verified after manual squash merge."
workflow:
  - id: required-check-recheck
    when: "The open pull request, approved head branch, head commit, and base branch passed the initial merge gate."
    skill: github-pr-check-validation
  - id: manual-squash-merge
    when: "The exact open pull request passed the immediate required-check recheck."
    ask: "Manually squash-merge this exact pull request in GitHub, then confirm completion for this unchanged head branch and head commit."
```

## Procedure

1. Before asking the user to merge, require open state, base `main`, mergeable status, ready state, and an exact match between the current head branch, head commit, and current-turn user decision context.
2. Invoke `github-pr-check-validation` immediately before requesting the manual squash merge, supplying this exact current head. Require its `passed` result.
3. Ask the user to manually squash-merge that exact pull request in GitHub and confirm completion. Never treat silence, approval alone, or an ambiguous response as confirmation.
4. Only after current-turn confirmation, run `python3 /code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py --pr <pr> --expected-head <approved head> --expected-branch <approved branch> --expected-base main`.
5. Require one versioned JSON result. Require every configured `origin` fetch and effective push URL and the non-cross-repository pull-request head to match the checkout GitHub repository. The script performs no merge or other mutation.
6. Return `waiting-user-merge` when confirmation was supplied but the exact pull request remains open and unchanged. Accept `user-merged` only when GitHub reports merged state, unchanged head, head branch, and base, plus a merged timestamp and merge commit.

## Boundaries

- Never parse or classify required checks outside `github-pr-check-validation`; never bypass its result or infer approval or merge completion.
- Never run `gh pr merge`, a merge API mutation, or any automatic merge. The user owns the manual squash merge; this skill only verifies the exact resulting GitHub state.
- Never delete a local or remote branch, worktree, or directory. Remote branch cleanup belongs to `github-pr-remote-branch-cleanup`.

## Completion

Report `user-merged`, `waiting-user-merge`, `waiting-external`, or `blocked-unsafe`; repository, pull-request URL, approved head and base branch, canonical required-check result, verified manual squash-merge evidence, and blocker.
