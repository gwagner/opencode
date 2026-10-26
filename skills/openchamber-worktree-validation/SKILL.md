---
name: openchamber-worktree-validation
description: Verifies that one existing OpenChamber-linked worktree is clean and ready for bounded work.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py *": allow
  external_directory:
    "/code/skills/openchamber-worktree-validation/scripts/validate-worktree.py": allow
inputs:
  - current OpenChamber-linked Git worktree
  - expected base branch
---

# OpenChamber worktree validation

## Inputs

Require the current OpenChamber-linked Git worktree and its expected base branch.

## Procedure

Run `python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py --base <base>`. It verifies only current worktree identity, an attached non-base branch, conflicts, and uncommitted changes. It does not fetch, merge, recover, or alter a worktree.

## Completion

Report `passed`, `waiting-user-cleanup`, or `blocked-unsafe` with branch and blocker.
