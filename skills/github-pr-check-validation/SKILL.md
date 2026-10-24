---
name: github-pr-check-validation
description: Classifies and boundedly rechecks required GitHub pull-request checks for one unchanged open pull request.
classification: technical
opencode_permission:
  shell:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh pr view * --json number,url,state,baseRefName,headRefName,headRefOid": allow
    "gh pr checks * --required --json bucket,name,state,workflow,link": allow
    "gh api --include repos/*/branches/*/protection": allow
    'gh api "repos/*/rulesets?includes_parents=true"': allow
    "sleep 30": allow
inputs:
  - one open GitHub pull request
  - expected pull-request head commit
  - authenticated GitHub CLI
---

# GitHub pull-request check validation

## Inputs

Require one open GitHub pull request, its expected head commit, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, and `gh pr view <pr> --json number,url,state,baseRefName,headRefName,headRefOid`. Require authentication, one repository, open state, the expected head commit, and nonempty head and base branches.
2. Run `gh pr checks <pr> --required --json bucket,name,state,workflow,link`, preserving its exit status, stdout, and stderr separately. Parse stdout as exactly one JSON array when nonempty. Record every check's name, workflow when present, link when present, bucket, and state.
3. Classify one nonempty parseable array as follows. A record is `passing` only with a nonempty `name`, `bucket` `pass`, and `state` `SUCCESS` or `NEUTRAL`. A record is `pending` only with a nonempty `name`, `bucket` `pending`, and `state` `QUEUED`, `PENDING`, `IN_PROGRESS`, or `WAITING`. A record is `failed` only with a nonempty `name` and one of these exact bucket/state pairs: `fail` with `FAILURE`, `ERROR`, `TIMED_OUT`, or `ACTION_REQUIRED`; `cancel` with `CANCELLED`; or `skipping` with `SKIPPED` or `STALE`. The array is `passing` only when exit status is `0` and every record is passing. It is `pending` only when exit status is the documented `8` for pending checks, every record is passing or pending, and at least one is pending. It is `failed` only when exit status is `1`, every record is passing, pending, or failed, and at least one is failed. All other output, fields, exit-status and record combinations, command failures, and JSON failures are `blocked`.
   failed, pending, cancelled, skipped-required, timed-out, unavailable, and ambiguous evidence never permits a pass; only a valid `pending` classification proceeds to the bounded recheck.
4. Classify an empty result as `passing` only when it is a zero-required-check candidate: either exit status `0`, stdout exactly one parseable JSON array `[]`, and empty stderr; or exit status `1`, empty stdout, and stderr is exactly `no required checks reported on the '<head branch>' branch` apart from its terminating newline, where `<head branch>` is the exact checked `headRefName`. For that candidate, verify configuration instead of accepting the CLI outcome alone: run `gh api --include repos/<owner>/<repo>/branches/<base branch>/protection` and require HTTP status `404` and a parseable JSON `message` exactly `Branch not protected`; then run `gh api "repos/<owner>/<repo>/rulesets?includes_parents=true"` and require a successful, parseable empty JSON array (`[]`). Only that combination verifies zero configured required checks for this repository and base branch. Any other empty result or configuration outcome is `blocked`.
5. After every check attempt, re-read the pull request. Require its state, head commit, head branch, and base branch to remain unchanged from step 1; otherwise classify the evidence as `blocked` and require a new invocation.
6. When classification is `pending`, run `sleep 30` and repeat steps 2 through 5. Make at most five such rechecks. Stop immediately on `passing`, `failed`, or `blocked`. When all five rechecks remain pending, report `blocked` with the pending deadline exhausted; never merge from pending evidence.

## Boundaries

- This skill is the sole owner of required-check parsing, classification, zero-configuration verification, and bounded pending rechecks.
- Never edit code, push, approve, merge, mutate issues, or infer hosted required-check evidence from local delegate validation.

## Completion

Report `passed` only for `passing` evidence, `failed` for terminal failed evidence, and `blocked` for malformed, unavailable, changed-head, zero-configuration ambiguity, or pending-deadline evidence. Report repository, pull-request URL, checked head and base branch, every attempt's classification, required-check stdout, stderr, and exit-status evidence, zero-configuration endpoint evidence when applicable, and failures.
