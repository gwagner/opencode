---
name: github-issue-reopen
description: Reopens one closed GitHub issue and verifies its open state.
classification: non-technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh issue view * --json number,title,state,url": allow
    "gh issue reopen *": allow
inputs:
  - one existing GitHub issue URL or number
  - current Git checkout for the issue repository
  - authenticated GitHub CLI
---

# GitHub issue reopen

## Inputs

Require one existing GitHub issue URL or number, the current Git checkout for its repository, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status` and `gh repo view --json nameWithOwner,url`. Stop unless authentication is available and the checkout resolves exactly one repository.
2. Read the issue with `gh issue view <issue> --json number,title,state,url`. Stop unless it belongs to the resolved repository.
3. If the issue is closed, run `gh issue reopen <issue>`. If it is already open, leave it unchanged.
4. Re-read the issue and require open state.

## Boundaries

- Never edit, comment on, label, close, or delete the issue.
- Never mutate an issue outside the repository resolved from the current checkout.

## Completion

Report the repository, issue URL, previous state, verified open state, and whether a mutation occurred.
