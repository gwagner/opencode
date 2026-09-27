---
name: github-pr-publication
description: Pushes committed issue work and creates its single GitHub pull request after recovery excludes an existing match.
classification: technical
opencode_permission:
  bash:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "git branch --show-current": allow
    "git status --porcelain=v1": allow
    "git rev-parse HEAD": allow
    "git push --set-upstream origin *": allow
    "git push origin *": allow
    "gh pr list --head * --state all --json number,state,url,title": allow
    "gh pr list --search * --state all --json number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt": allow
    "gh pr create --base main --head * --title * --body-file /tmp/opencode/github-sdlc-pr.md": allow
    "gh pr view * --json number,title,url,state,baseRefName,headRefName,headRefOid": allow
    "rm -f /tmp/opencode/github-sdlc-pr.md": allow
  external_directory:
    "/tmp/opencode/github-sdlc-pr.md": allow
  edit:
    "/tmp/opencode/github-sdlc-pr.md": allow
inputs:
  - originating GitHub issue identity
  - lifecycle-recovery disposition reporting no matching pull request
  - current non-main feature branch
  - one or more reviewed task commits
  - caller-provided pull-request title and summary
  - authenticated GitHub CLI
---

# GitHub pull-request publication

## Inputs

Require the originating GitHub issue identity, a lifecycle-recovery disposition reporting no matching pull request, the current non-`main` feature branch, one or more reviewed task commits, a caller-provided pull-request title and summary, and an authenticated GitHub CLI.

## Procedure

1. Require lifecycle recovery to report the unique no-pull-request fresh-start state. Otherwise stop: the matching GitHub pull request is authoritative and publication must not use local Git to override it.
2. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, `git branch --show-current`, `git status --porcelain=v1`, and `git rev-parse HEAD`. Require authentication, one repository, a clean non-`main` branch, and the expected committed head.
3. Run `gh pr list --search "Refs #<originating issue> in:body" --state all --json number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt`. Treat a matching pull request as one whose body contains the exact standalone line `Refs #<originating issue>`. Stop unless the result is empty; lifecycle recovery owns all existing-match routing.
4. Run `gh pr list --head <branch> --state all --json number,state,url,title`. Stop on any result; a pull request not identified by the required issue reference is ambiguous and must not be reused.
5. For no existing match, write the approved summary, validation evidence, and `Refs #<originating issue>` to `/tmp/opencode/github-sdlc-pr.md`. Do not use an automatic-closing keyword because issue closure occurs only after the approved merge and completion comment.
6. Push with `git push --set-upstream origin <branch>` and create the pull request with `gh pr create --base main --head <branch> --title <title> --body-file /tmp/opencode/github-sdlc-pr.md`.
7. Verify the pull request with `gh pr view <pr> --json number,title,url,state,baseRefName,headRefName,headRefOid`. Require open state, base `main`, the exact head branch, and expected head commit.
8. Run `rm -f /tmp/opencode/github-sdlc-pr.md` after success or failure. Report cleanup failure as a blocker.

## Boundaries

- Never force-push, change branches, merge, close a pull request, or mutate the originating issue.
- Never publish uncommitted or unvalidated work.

## Completion

Report repository, branch, pushed head, pull-request URL, whether it was created or reused, and cleanup status.
