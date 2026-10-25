---
name: github-pr-remote-branch-cleanup
description: Deletes one verified merged pull request's unchanged remote branch and confirms its absence.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-remote-branch-cleanup/scripts/cleanup-remote-branch.py *": allow
  external_directory:
    "/code/skills/github-pr-remote-branch-cleanup/scripts/cleanup-remote-branch.py": allow
inputs:
  - one verified merged pull request
  - exact merged head and base branch
  - expected GitHub repository from the current checkout
  - provenance: cli, openchamber, or github-issue
  - originating issue number required for github-issue provenance
  - authenticated GitHub CLI
---

# GitHub pull-request remote branch cleanup

## Inputs

Require one verified merged pull request, its exact merged head and base branch, the expected GitHub repository from the current checkout, provenance `cli`, `openchamber`, or `github-issue`, the originating issue number exactly for `github-issue`, and an authenticated GitHub CLI.

## Procedure

1. Run `python3 /code/skills/github-pr-remote-branch-cleanup/scripts/cleanup-remote-branch.py --pr <pr> --expected-head <head> --expected-base <base> --provenance <provenance> [--issue <issue>]`.
2. Require one versioned JSON result. Accept `already-absent` or `deleted` only after verifying that every configured Git remote `origin` fetch and effective push URL matches the checkout GitHub repository, the pull request is not cross-repository, its head repository matches `origin`, and merged state, unchanged PR identity, exactly one matching provenance marker, expected-head conditional deletion, and remote-branch absence are verified. Non-issue provenance permits no `Refs #` marker; issue provenance requires exactly one marker for the supplied issue.
3. Return `waiting-external` for authentication, network, GitHub availability, deletion failure with an unchanged ref, or an unconfirmed deletion. If the leased delete fails but the verified branch is subsequently absent, return `already-absent`, not lifecycle-owned `deleted`. Return `blocked-unsafe` for malformed output, changed identity, changed ref, base-branch deletion, or provenance mismatch.

## Boundaries

- Delete only the merged pull request's remote head branch with an exact expected-head lease, so a concurrent ref change rejects the deletion.
- Never inspect or delete a branch until every configured Git remote `origin` fetch and effective push URL resolves to the same host and repository identity as the verified GitHub repository.
- Never delete or switch a local branch, mutate a worktree, merge, close a pull request, or mutate an issue.

## Completion

Report `already-absent`, `deleted`, `waiting-external`, or `blocked-unsafe`; repository, pull request, head, base, branch, remote-ref evidence, deletion result, and blocker.
