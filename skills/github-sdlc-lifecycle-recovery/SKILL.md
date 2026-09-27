---
name: github-sdlc-lifecycle-recovery
description: Selects the one safe GitHub-authoritative resume point for an issue-originated SDLC lifecycle.
classification: technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh issue view * --json number,title,state,url,comments": allow
    "gh pr list --search * --state all --json number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt": allow
    "gh pr view * --json number,title,url,state,body,baseRefName,headRefName,headRefOid,mergedAt,mergeCommit": allow
inputs:
  - originating GitHub issue URL or number
  - expected GitHub repository from the current checkout
  - authenticated GitHub CLI
---

# GitHub SDLC lifecycle recovery

## Inputs

Require the originating GitHub issue URL or number, the expected GitHub repository from the current checkout, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status` and `gh repo view --json nameWithOwner,url`. Stop unless authentication is available and the checkout resolves exactly one repository.
2. Run `gh issue view <issue> --json number,title,state,url,comments`. Stop unless the issue belongs to the resolved repository. If the issue is closed, return `blocked` as an already-terminal lifecycle and do not resume or mutate it.
3. Run `gh pr list --search "Refs #<issue> in:body" --state all --json number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt`. A match has the exact standalone body line `Refs #<issue>`, base branch `main`, nonempty head branch and head commit, and a state of `OPEN` or `MERGED`. Reject any other state, malformed candidate, or more than one match. GitHub is authoritative: never consult local branch, HEAD, or worktree state to select a matching pull request.
4. When the open issue has no match, return `fresh-start`. This is the only result that permits local issue-worktree validation, baseline capture, implementation, commit, and publication.
5. When the issue is open and exactly one matching pull request is open, return `open-pull-request` with its URL, base branch, head branch, and head commit. Resume at hosted required-check validation; do not perform local worktree validation, baseline capture, implementation, commit, or publication.
6. When the issue is open and exactly one matching pull request is merged, re-read it with `gh pr view <pr> --json number,title,url,state,body,baseRefName,headRefName,headRefOid,mergedAt,mergeCommit`. Require `MERGED`, base `main`, nonempty merged time, nonempty head commit, and nonempty merge commit. In the issue comments, require exactly one current pre-closure evidence comment containing `Lifecycle evidence: current`, the exact pull-request URL, `Head commit: <head commit>`, `Delegate project-validation: passed`, and `Required checks: passed`.
7. For that merged state, count recovery pre-closure comments containing `Lifecycle recovery: merged-pr`, the exact pull-request URL, and `Head commit: <head commit>`; count completion comments containing `Lifecycle completion: merged-pr`, the exact pull-request URL, and `Head commit: <head commit>`. Reject more than one of either kind. Return `merged-needs-pre-closure` when neither exists, `merged-needs-completion` when exactly one recovery pre-closure exists and no completion exists, or `merged-needs-close` when exactly one of each exists. These are the only merged-state resume points. Do not rerun local validation or represent retained evidence as newly executed.
8. Return `blocked` for every other state, including a merged pull request without retained evidence, a missing or multiple match, or conflicting identifiers. Report the observed issue state, candidate pull-request URLs and states, the missing invariant, and the next manual action. Never mutate GitHub, Git, branches, or worktrees.

## Boundaries

- This skill selects a resume point; it does not validate checks, post comments, close issues, push, merge, edit files, or run local Git commands.
- Never infer a matching pull request from a title, branch name, comment URL, or local Git state.
- Never create, remove, prune, move, repair, or switch a worktree or branch.

## Completion

Report `fresh-start`, `open-pull-request`, `merged-needs-pre-closure`, `merged-needs-completion`, `merged-needs-close`, or `blocked`; repository, issue URL and state, matching pull-request URL and state when present, head and merge commits when present, retained-evidence result, exact next stage, and blockers.
