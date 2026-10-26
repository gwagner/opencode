---
name: github-issue-close
description: Closes one user-selected GitHub issue.
classification: technical
opencode_permission:
  shell:
    "gh issue close *": allow
inputs:
  - exact existing issue identity
  - explicit user request to close it
---

# GitHub issue closure

## Inputs

Require an exact existing issue identity and an explicit user request to close it.

## Procedure

Run `gh issue close <issue>`. It performs one GitHub closure request and does not infer closure from a pull request or other workflow state.

## Completion

Report the command result.
