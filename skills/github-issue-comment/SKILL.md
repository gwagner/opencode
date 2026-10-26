---
name: github-issue-comment
description: Posts one user-requested comment to an existing GitHub issue.
classification: technical
opencode_permission:
  bash:
    "gh issue comment * --body-file /tmp/opencode/github-issue-manager-comment.md": allow
  external_directory:
    /tmp/opencode/github-issue-manager-comment.md: allow
  read:
    "/tmp/opencode/github-issue-manager-comment.md": allow
  edit:
    "/tmp/opencode/github-issue-manager-comment.md": allow
inputs:
  - exact existing issue identity
  - caller-provided comment body
  - explicit user request to post it
---

# GitHub issue comment

## Inputs

Require an exact existing issue identity, a caller-provided comment body, and an explicit user request to post it.

## Procedure

Write the body to `/tmp/opencode/github-issue-manager-comment.md`, then run `gh issue comment <issue> --body-file /tmp/opencode/github-issue-manager-comment.md`. The command posts the body as data.

## Completion

Report the posted comment URL or command failure.
