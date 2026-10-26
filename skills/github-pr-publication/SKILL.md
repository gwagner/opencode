---
name: github-pr-publication
description: Pushes one validated committed branch and creates a draft GitHub pull request on explicit request.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-publication/scripts/publish-pr.py *": allow
  external_directory:
    "/code/skills/github-pr-publication/scripts/publish-pr.py": allow
  read: allow
inputs:
  - explicit user request to publish
  - clean committed non-base branch
  - pull-request title
  - caller-provided readable pull-request body file
  - authenticated GitHub CLI
---

# GitHub pull-request publication

## Inputs

Require an explicit user publication request, a clean committed non-base branch, a title, a caller-provided readable pull-request body file, and an authenticated GitHub CLI. The caller restricts the body-file path at runtime.

## Procedure

Run `python3 /code/skills/github-pr-publication/scripts/publish-pr.py --title <title> --body-file <caller-permitted-path> --base <base>`. The script pushes the current branch and creates one draft pull request. If GitHub reports an existing pull request, report that result rather than recovering or changing it.

## Boundaries

Never infer publication from implementation. Never merge, close issues, delete branches, or retry uncertain remote operations.

## Completion

Report the pull-request URL or the exact command failure.
