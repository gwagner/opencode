---
name: feature-branch-setup
description: Creates one clean local feature branch before a bounded coding change.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/feature-branch-setup/scripts/setup-feature-branch.py *": allow
  external_directory:
    "/code/skills/feature-branch-setup/scripts/setup-feature-branch.py": allow
inputs:
  - bounded requested outcome
  - clean Git worktree on the caller-selected base branch
---

# Feature branch setup

## Inputs

Require a bounded requested outcome and a clean Git worktree on the caller-selected base branch.

## Procedure

Run `python3 /code/skills/feature-branch-setup/scripts/setup-feature-branch.py --outcome <outcome> --base <base>`. It creates one unused `feature/<slug>` branch. It does not fetch, push, reuse a branch, or change unrelated work.

## Completion

Report the branch and base revision, or the exact blocker.
