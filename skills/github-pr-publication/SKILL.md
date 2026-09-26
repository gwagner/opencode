---
name: github-pr-publication
description: Pushes committed issue work and creates or returns its single open GitHub pull request.
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
    "gh pr create --base main --head * --title * --body-file /tmp/opencode/github-sdlc-pr.md": allow
    "gh pr view * --json number,title,url,state,baseRefName,headRefName,headRefOid": allow
    "rm -f /tmp/opencode/github-sdlc-pr.md": allow
  external_directory:
    "/tmp/opencode/github-sdlc-pr.md": allow
  edit:
    "/tmp/opencode/github-sdlc-pr.md": allow
inputs:
  - originating GitHub issue identity
  - current non-main feature branch
  - one or more reviewed task commits
  - caller-provided pull-request title and summary
  - authenticated GitHub CLI
---

# GitHub pull-request publication

## Inputs

Require the originating GitHub issue identity, the current non-`main` feature branch, one or more reviewed task commits, a caller-provided pull-request title and summary, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, `git branch --show-current`, `git status --porcelain=v1`, and `git rev-parse HEAD`. Require authentication, one repository, a clean non-`main` branch, and the expected committed head.
2. Run `gh pr list --head <branch> --state all --json number,state,url,title`. Stop on multiple matching pull requests or a closed or merged match. If one open match exists, push the current head with `git push origin <branch>`, verify it, and return that pull request.
3. For no existing match, write the approved summary, validation evidence, and `Refs #<originating issue>` to `/tmp/opencode/github-sdlc-pr.md`. Do not use an automatic-closing keyword because issue closure occurs only after the approved merge and completion comment.
4. Push with `git push --set-upstream origin <branch>` and create the pull request with `gh pr create --base main --head <branch> --title <title> --body-file /tmp/opencode/github-sdlc-pr.md`.
5. Verify the pull request with `gh pr view <pr> --json number,title,url,state,baseRefName,headRefName,headRefOid`. Require open state, base `main`, the exact head branch, and expected head commit.
6. Run `rm -f /tmp/opencode/github-sdlc-pr.md` after success or failure. Report cleanup failure as a blocker.

## Boundaries

- Never force-push, change branches, merge, close a pull request, or mutate the originating issue.
- Never publish uncommitted or unvalidated work.

## Completion

Report repository, branch, pushed head, pull-request URL, whether it was created or reused, and cleanup status.
