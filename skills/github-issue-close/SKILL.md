---
name: github-issue-close
description: Closes one user-selected GitHub issue.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-issue-close/scripts/close-issue.py *": allow
  external_directory:
    "/code/skills/github-issue-close/scripts/close-issue.py": allow
inputs:
  - exact existing issue identity
  - explicit user request to close it
---

# GitHub issue closure

## Inputs

Require an exact existing issue identity and an explicit user request to close it.

## Procedure

Run `python3 /code/skills/github-issue-close/scripts/close-issue.py --issue <issue>`. The script performs one GitHub closure request. It does not infer closure from a pull request or other workflow state.

## Completion

Report the command result.
