---
name: github-pr-publication
description: Pushes one validated committed branch and creates a draft GitHub pull request on explicit request.
classification: technical
opencode_permission:
  bash:
    "python3 /code/skills/github-pr-publication/scripts/publish-pr.py *": ask
  read: allow
inputs:
  - caller-provided permitted read paths
  - explicit user request to publish
  - clean committed non-base branch
  - pull-request title
  - caller-provided readable pull-request body file
  - authenticated GitHub CLI
---

# GitHub pull-request publication

## Inputs

Require caller-provided permitted read paths.

Require an explicit user publication request, a clean committed non-base branch, a title, a caller-provided readable pull-request body file, and an authenticated GitHub CLI. The caller restricts the body-file path at runtime.

## Procedure

Run `python3 /code/skills/github-pr-publication/scripts/publish-pr.py --title <title> --body-file <caller-permitted-path> --base <base>`. OpenCode must present its native `ask` approval for that publication command before it runs. The script verifies that `origin` matches the GitHub repository, binds pull-request queries and creation to that repository, pushes the current branch, and creates one draft pull request. If GitHub reports an existing pull request, report that result rather than recovering or changing it. If the push succeeds but creation fails, report `branch-pushed; pull-request-not-created` as a partial publication and do not retry or recover it.

## Boundaries

Never infer publication from implementation. Never merge, close issues, delete branches, or retry uncertain remote operations.

## Completion

Report the pull-request URL or the exact command failure.
