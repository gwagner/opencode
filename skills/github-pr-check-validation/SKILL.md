---
name: github-pr-check-validation
description: Waits for and verifies all required checks on one open GitHub pull request.
classification: technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh pr view * --json number,url,state,headRefOid": allow
    "gh pr checks * --required --watch --json bucket,name,state,workflow,link": allow
inputs:
  - one open GitHub pull request
  - expected pull-request head commit
  - authenticated GitHub CLI
---

# GitHub pull-request check validation

## Inputs

Require one open GitHub pull request, its expected head commit, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, and `gh pr view <pr> --json number,url,state,headRefOid`. Require authentication, one repository, open state, and the expected head commit.
2. Run `gh pr checks <pr> --required --watch --json bucket,name,state,workflow,link`. Require a successful command and one parseable JSON array. A successful empty array (`[]`) is a verified empty required-check set and passes. For every returned required-check record, require a nonempty `name`, `bucket` equal to `pass`, and `state` equal to `SUCCESS` or `NEUTRAL`. Treat a command or JSON failure, a missing or unknown field, or any other bucket or state as `blocked`; this includes failed, pending, cancelled, skipped-required, timed-out, unavailable, and ambiguous evidence. Record each check's name, workflow when present, link when present, bucket, and state.
3. Re-read the pull request and require the head commit to remain unchanged. A changed head invalidates the check evidence and requires a new invocation.

## Boundaries

- Never rerun checks, edit code, push, approve, merge, or mutate issues.
- Never treat local delegate validation as hosted required-check evidence.

## Completion

Report `passed` or `blocked`, repository, pull-request URL, checked head commit, required-check JSON evidence (including `[]` when empty), and failures.
