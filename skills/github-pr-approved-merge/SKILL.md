---
name: github-pr-approved-merge
description: Squash-merges one fully checked GitHub pull request after head-specific user approval and deletes only its remote branch.
classification: technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh pr view * --json number,url,state,mergeable,baseRefName,headRefName,headRefOid": allow
    "gh pr checks * --required --json bucket,name,state,workflow,link": allow
    "gh api --include repos/*/branches/*/protection": allow
    'gh api "repos/*/rulesets?includes_parents=true"': allow
    "gh pr merge * --squash --match-head-commit *": allow
    "git ls-remote --heads origin *": allow
    "git push origin --delete *": allow
inputs:
  - one open GitHub pull request targeting main
  - passed required-check evidence for the current head and base branch
  - explicit user merge approval for the exact pull request and head commit
  - authenticated GitHub CLI
---

# GitHub approved pull-request merge

## Inputs

Require one open GitHub pull request targeting `main`, passed required-check evidence for its current head and base branch, explicit user merge approval naming the exact pull request and head commit, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, and `gh pr view <pr> --json number,url,state,mergeable,baseRefName,headRefName,headRefOid`.
2. Require open state, base `main`, mergeable status, and an exact match between the current head, passed check evidence, and current-turn user approval. Stop if any value differs.
3. Run `gh pr checks <pr> --required --json bucket,name,state,workflow,link`, preserving its exit status, stdout, and stderr separately. For a nonempty parseable JSON array, require exit status `0`, a nonempty `name` on every record, `bucket` equal to `pass`, and `state` equal to `SUCCESS` or `NEUTRAL` on every record. Record each check's name, workflow when present, link when present, bucket, and state.
4. Treat a result as a zero-required-check candidate only when either (a) exit status is `0`, stdout is exactly one parseable JSON array `[]`, and stderr is empty, or (b) exit status is `1`, stdout is empty, and stderr is exactly `no required checks reported on the '<base branch>' branch` apart from its terminating newline. Any command or JSON failure outside that known outcome, missing or unknown field, or any other bucket or state is `blocked`; this includes failed, pending, cancelled, skipped-required, timed-out, unavailable, and ambiguous evidence.
5. For a zero-required-check candidate, verify configuration instead of accepting the CLI outcome alone. Run `gh api --include repos/<owner>/<repo>/branches/<base branch>/protection` and require HTTP status `404` and a parseable JSON `message` exactly `Branch not protected`; do not infer absent protection from an exit status or error string alone. Run `gh api "repos/<owner>/<repo>/rulesets?includes_parents=true"` and require a successful, parseable empty JSON array (`[]`). Only that combination verifies zero configured required checks for this repository and base branch. A protection response other than `404`, a nonempty ruleset list, an unavailable endpoint, an unparseable response, or any other configuration ambiguity is `blocked`.
6. Re-read the pull request. Require open state, base `main`, mergeable status, and an exact match between its head, the approved head, and the passed-check evidence. Stop if the head or any gate changed.
7. Run `gh pr merge <pr> --squash --match-head-commit <approved head>` once. Re-read the pull request and require merged state before cleanup.
8. Run `git ls-remote --heads origin <head branch>`. If the branch remains, delete it with `git push origin --delete <head branch>`, then require a second `git ls-remote --heads origin <head branch>` to return no ref. Never delete or switch the local branch or worktree. Report remote cleanup failure separately without obscuring a successful merge.

## Boundaries

- Never bypass checks, use administrative merge, infer approval, merge a changed head, or merge into a base other than `main`.
- Never delete a local branch, worktree, or directory.

## Completion

Report repository, pull-request URL, approved head and base branch, required-check stdout, stderr, and exit-status evidence, zero-configuration endpoint evidence when applicable, squash-merge result, and remote-branch deletion result.
