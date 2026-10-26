---
name: github-issue-comment
description: Posts one user-requested comment to an existing GitHub issue.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-issue-comment/scripts/post-comment.py *": allow
  read:
    "/tmp/opencode/github-issue-manager-comment.md": allow
  edit:
    "/tmp/opencode/github-issue-manager-comment.md": allow
  external_directory:
    "/code/skills/github-issue-comment/scripts/post-comment.py": allow
inputs:
  - exact existing issue identity
  - caller-provided comment body
  - explicit user request to post it
---

# GitHub issue comment

## Inputs

Require an exact existing issue identity, a caller-provided comment body, and an explicit user request to post it.

## Procedure

Write the body to `/tmp/opencode/github-issue-manager-comment.md`, then run `python3 /code/skills/github-issue-comment/scripts/post-comment.py --issue <issue>`. The script posts the body as data.

## Completion

Report the posted comment URL or command failure.
