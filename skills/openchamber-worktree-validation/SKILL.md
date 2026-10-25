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
  - execution mode: fresh, resume-publication, or resume-pull-request
  - current OpenChamber-linked Git worktree
  - expected base branch
  - expected task head when resuming
---

# OpenChamber worktree validation

## Inputs

Require execution mode `fresh`, `resume-publication`, or `resume-pull-request`, the current OpenChamber-linked Git worktree, the expected base branch, and the expected task head in either resume mode.

## Procedure

1. Run `python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py --mode <mode> --base <base> [--expected-head <head>]` from the current worktree.
2. Require one versioned JSON result.
3. In fresh mode, use refreshed-base ancestry and `origin/main..HEAD` range evidence: a clean feature branch at an older main ancestor with zero feature commits is eligible, while any unestablished feature commit is `blocked-unsafe`. Continue to ownership baseline on `passed` or `resume-pull-request`. Continue only to PR publication on `resume-publication`. Classify unresolved conflicts separately as `blocked-unsafe`; return `waiting-user-cleanup` for ordinary unrelated dirt. Stop on other `blocked-unsafe` identity, topology, detached-head, or ownership ambiguity.
4. Preserve all observed work. Never reset, restore, clean, stash, create, remove, prune, move, or switch a worktree or branch.

## Completion

Report the disposition, root, branch, head, base revision, clean state, linked-worktree evidence, and blocker.
