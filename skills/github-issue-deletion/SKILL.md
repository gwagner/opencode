---
name: github-issue-deletion
description: Permanently deletes one GitHub issue only after explicit issue-specific confirmation.
classification: non-technical
opencode_permission:
  question: allow
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh issue view * --json number,title,state,url": allow
    "gh issue delete * --yes": allow
inputs:
  - one existing GitHub issue URL or number
  - current Git checkout for the issue repository
  - explicit permanent-deletion request
  - authenticated GitHub CLI
---

# GitHub issue deletion

## Inputs

Require one existing GitHub issue URL or number, the current Git checkout for its repository, an explicit permanent-deletion request, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status` and `gh repo view --json nameWithOwner,url`. Stop unless authentication is available and the checkout resolves exactly one repository.
2. Read the issue with `gh issue view <issue> --json number,title,state,url`. Stop unless it belongs to the resolved repository.
3. Ask for confirmation that names the repository, issue number, title, URL, and irreversible loss of issue history. Continue only when the user explicitly confirms permanent deletion of that exact issue in the current turn.
4. Run `gh issue delete <issue> --yes` once. Do not retry an ambiguous response.
5. Verify that `gh issue view <issue> --json number,title,state,url` no longer resolves the issue. If it still resolves or the result is ambiguous, report `blocked` and do not attempt another deletion.

## Boundaries

- Never infer deletion from “close”, cleanup, completion, deduplication, or archival language.
- Never delete an issue outside the repository resolved from the current checkout.

## Completion

Report the repository, deleted issue identity, confirmation evidence, deletion result, and any ambiguity.
