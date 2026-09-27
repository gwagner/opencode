---
name: github-pr-check-validation
description: Verifies all required checks on one open GitHub pull request.
classification: technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh pr view * --json number,url,state,baseRefName,headRefOid": allow
    "gh pr checks * --required --json bucket,name,state,workflow,link": allow
    "gh api --include repos/*/branches/*/protection": allow
    'gh api "repos/*/rulesets?includes_parents=true"': allow
inputs:
  - one open GitHub pull request
  - expected pull-request head commit
  - authenticated GitHub CLI
---

# GitHub pull-request check validation

## Inputs

Require one open GitHub pull request, its expected head commit, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, and `gh pr view <pr> --json number,url,state,baseRefName,headRefOid`. Require authentication, one repository, open state, the expected head commit, and a nonempty base branch.
2. Run `gh pr checks <pr> --required --json bucket,name,state,workflow,link`, preserving its exit status, stdout, and stderr separately. For a nonempty parseable JSON array, require exit status `0`, a nonempty `name` on every record, `bucket` equal to `pass`, and `state` equal to `SUCCESS` or `NEUTRAL` on every record. Record each check's name, workflow when present, link when present, bucket, and state.
3. Treat a result as a zero-required-check candidate only when either (a) exit status is `0`, stdout is exactly one parseable JSON array `[]`, and stderr is empty, or (b) exit status is `1`, stdout is empty, and stderr is exactly `no required checks reported on the '<base branch>' branch` apart from its terminating newline. Any command or JSON failure outside that known outcome, missing or unknown field, or any other bucket or state is `blocked`; this includes failed, pending, cancelled, skipped-required, timed-out, unavailable, and ambiguous evidence.
4. For a zero-required-check candidate, verify configuration instead of accepting the CLI outcome alone. Run `gh api --include repos/<owner>/<repo>/branches/<base branch>/protection` and require HTTP status `404` and a parseable JSON `message` exactly `Branch not protected`; do not infer absent protection from an exit status or error string alone. Run `gh api "repos/<owner>/<repo>/rulesets?includes_parents=true"` and require a successful, parseable empty JSON array (`[]`). Only that combination verifies zero configured required checks for this repository and base branch. A protection response other than `404`, a nonempty ruleset list, an unavailable endpoint, an unparseable response, or any other configuration ambiguity is `blocked`.
5. Re-read the pull request and require the head commit and base branch to remain unchanged. A changed head or base invalidates the check evidence and requires a new invocation.

## Boundaries

- Never rerun checks, edit code, push, approve, merge, or mutate issues.
- Never treat local delegate validation as hosted required-check evidence.

## Completion

Report `passed` or `blocked`, repository, pull-request URL, checked head and base branch, required-check stdout, stderr, and exit-status evidence, zero-configuration endpoint evidence when applicable, and failures.
