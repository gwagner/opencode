---
name: openchamber-worktree-validation
description: Classifies and safely prepares one existing OpenChamber-linked worktree for fresh or resumed SDLC execution.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py *": allow
  external_directory:
    "/code/skills/openchamber-worktree-validation/scripts/validate-worktree.py": allow
inputs:
  - execution mode: fresh or resume
  - current OpenChamber-linked Git worktree
  - expected base branch
  - expected task head when resuming
---

# OpenChamber worktree validation

## Inputs

Require execution mode `fresh` or `resume`, the current OpenChamber-linked Git worktree, the expected base branch, and the expected task head when resuming.

## Procedure

1. Run `python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py --mode <mode> --base <base> [--expected-head <head>]` from the current worktree.
2. Require one versioned JSON result.
3. Continue on `passed`. Continue to PR publication on `resume-publication`. Return `waiting-user-cleanup` for unrelated dirty paths. Stop on `blocked-unsafe` identity, topology, detached-head, conflict, or ownership ambiguity.
4. Preserve all observed work. Never reset, restore, clean, stash, create, remove, prune, move, or switch a worktree or branch.

## Completion

Report the disposition, root, branch, head, base revision, clean state, linked-worktree evidence, and blocker.
