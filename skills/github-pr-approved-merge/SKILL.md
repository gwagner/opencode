---
name: github-pr-approved-merge
description: Squash-merges one user-approved GitHub pull request after canonical required-check validation of its unchanged head and deletes only its remote branch.
classification: technical
opencode_permission:
  shell:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh pr view * --json number,url,state,mergeable,baseRefName,headRefName,headRefOid": allow
    "gh pr merge * --squash --match-head-commit *": allow
    "git ls-remote --heads origin *": allow
    "git push origin --delete *": allow
  skill:
    github-pr-check-validation: allow
inputs:
  - one open GitHub pull request targeting main
  - explicit user merge approval for the exact pull request and head commit
  - authenticated GitHub CLI
---

# GitHub approved pull-request merge

## Inputs

Require one open GitHub pull request targeting `main`, explicit user merge approval naming the exact pull request and head commit, and an authenticated GitHub CLI.

## Workflow

```yaml
request: "One squash-merged, user-approved pull request with only its remote branch deleted."
workflow:
  - id: required-check-recheck
    when: "The open pull request, approved head, and base branch have passed the initial merge gate."
    skill: github-pr-check-validation
```

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, and `gh pr view <pr> --json number,url,state,mergeable,baseRefName,headRefName,headRefOid`.
2. Require open state, base `main`, mergeable status, and an exact match between the current head and current-turn user approval. Stop if any value differs.
3. Invoke `github-pr-check-validation` immediately before merging, supplying this exact current head. Require its `passed` result.
4. Re-read the pull request with `gh pr view <pr> --json number,url,state,mergeable,baseRefName,headRefName,headRefOid`. Require open state, base `main`, mergeable status, and unchanged head commit, head branch, and base branch that exactly match the approved head. Stop if any gate changed.
5. Run `gh pr merge <pr> --squash --match-head-commit <approved head>` once. Re-read the pull request and require merged state before cleanup.
6. Run `git ls-remote --heads origin <head branch>`. If the branch remains, delete it with `git push origin --delete <head branch>`, then require a second `git ls-remote --heads origin <head branch>` to return no ref. Never delete or switch the local branch or worktree. Report remote cleanup failure separately without obscuring a successful merge.

## Boundaries

- Never parse, classify, or recheck required checks outside `github-pr-check-validation`; never bypass its result, use administrative merge, infer approval, merge a changed head, or merge into a base other than `main`.
- Never delete a local branch, worktree, or directory.

## Completion

Report repository, pull-request URL, approved head and base branch, canonical required-check result, squash-merge result, and remote-branch deletion result.
