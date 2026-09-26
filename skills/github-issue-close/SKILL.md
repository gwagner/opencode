---
name: github-issue-close
description: Closes one existing GitHub issue and verifies its closed state.
classification: non-technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh issue view * --json number,title,state,url": allow
    "gh issue close *": allow
inputs:
  - one existing GitHub issue URL or number
  - current Git checkout for the issue repository
  - authenticated GitHub CLI
---

# GitHub issue close

## Inputs

Require one existing GitHub issue URL or number, the current Git checkout for its repository, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status` and `gh repo view --json nameWithOwner,url`. Stop unless authentication is available and the checkout resolves exactly one repository.
2. Read the issue with `gh issue view <issue> --json number,title,state,url`. Stop unless it belongs to the resolved repository.
3. If the issue is open, run `gh issue close <issue>`. If it is already closed, leave it unchanged.
4. Re-read the issue and require closed state.

## Boundaries

- Never edit, comment on, label, reopen, or delete the issue.
- Never mutate an issue outside the repository resolved from the current checkout.

## Completion

Report the repository, issue URL, previous state, verified closed state, and whether a mutation occurred.
