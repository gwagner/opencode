---
name: github-pr-approved-merge
description: Squash-merges one fully checked GitHub pull request after head-specific user approval and deletes only its remote branch.
classification: technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh pr view * --json number,url,state,mergeable,baseRefName,headRefName,headRefOid": allow
    "gh pr checks * --required": allow
    "gh pr merge * --squash --match-head-commit *": allow
    "git ls-remote --heads origin *": allow
    "git push origin --delete *": allow
inputs:
  - one open GitHub pull request targeting main
  - passed required-check evidence for the current head
  - explicit user merge approval for the exact pull request and head commit
  - authenticated GitHub CLI
---

# GitHub approved pull-request merge

## Inputs

Require one open GitHub pull request targeting `main`, passed required-check evidence for its current head, explicit user merge approval naming the exact pull request and head commit, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, and `gh pr view <pr> --json number,url,state,mergeable,baseRefName,headRefName,headRefOid`.
2. Require open state, base `main`, mergeable status, and an exact match between the current head, passed check evidence, and current-turn user approval. Stop if any value differs.
3. Run `gh pr checks <pr> --required` and require every required check still passes.
4. Run `gh pr merge <pr> --squash --match-head-commit <approved head>` once. Re-read the pull request and require merged state before cleanup.
5. Run `git ls-remote --heads origin <head branch>`. If the branch remains, delete it with `git push origin --delete <head branch>`, then require a second `git ls-remote --heads origin <head branch>` to return no ref. Never delete or switch the local branch or worktree. Report remote cleanup failure separately without obscuring a successful merge.

## Boundaries

- Never bypass checks, use administrative merge, infer approval, merge a changed head, or merge into a base other than `main`.
- Never delete a local branch, worktree, or directory.

## Completion

Report repository, pull-request URL, approved head, squash-merge result, and remote-branch deletion result.
