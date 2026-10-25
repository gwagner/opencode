---
name: openchamber-worktree-validation
description: Classifies and safely prepares one existing OpenChamber-linked worktree for fresh or resumed SDLC execution.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.json": allow
    "/code/skills/openchamber-worktree-validation/scripts/validate-worktree.py": allow
inputs:
  - optional `/tmp/opencode/lifecycle-policy.json`
  - execution mode: fresh, resume-publication, or resume-pull-request
  - current OpenChamber-linked Git worktree
  - expected base branch
  - expected task head when resuming
---

# OpenChamber worktree validation

## Inputs

Require execution mode `fresh`, `resume-publication`, or `resume-pull-request`, the current OpenChamber-linked Git worktree, an optional `/tmp/opencode/lifecycle-policy.json`, the expected policy base branch, and the expected task head in either resume mode.

## Procedure

1. Run `python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py --mode <mode> [--base <policy-base>] [--expected-head <head>] [--policy /tmp/opencode/lifecycle-policy.json]` from the current worktree.
2. Require one versioned JSON result.
3. In fresh mode, use refreshed policy-remote/policy-base ancestry and range evidence: a clean feature branch at an older main ancestor with zero feature commits is eligible under the default policy (or an older policy-base ancestor under an override), while any unestablished feature commit is `blocked-unsafe`. Continue to ownership baseline on `passed` or `resume-pull-request`. Continue only to PR publication on `resume-publication`. Classify unresolved conflicts separately as `blocked-unsafe`; return `waiting-user-cleanup` for ordinary unrelated dirt. Stop on other `blocked-unsafe` identity, topology, detached-head, or ownership ambiguity.
4. Preserve all observed work. Never reset, restore, clean, stash, create, remove, prune, move, or switch a worktree or branch.

## Completion

Report the disposition, root, branch, head, base revision, clean state, linked-worktree evidence, and blocker.
