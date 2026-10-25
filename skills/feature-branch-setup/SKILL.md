---
name: feature-branch-setup
description: Creates one clean local policy-selected feature branch before a bounded SDLC change.
classification: technical
opencode_permission:
  read:
    "/tmp/opencode/lifecycle-policy.json": allow
  shell:
    "git status --porcelain=v1*": allow
    "git rev-parse *": allow
    "git branch --show-current": allow
    "git branch --list *": allow
    "git switch -c * *": allow
    "python3 /code/skills/feature-branch-setup/scripts/setup-feature-branch.py *": allow
inputs:
  - bounded requested outcome
  - clean policy-base Git worktree
  - optional `/tmp/opencode/lifecycle-policy.json`
---

# Feature branch setup

## Inputs

Require a bounded requested outcome, a clean policy-base Git worktree, and an optional `/tmp/opencode/lifecycle-policy.json`. When supplied, require the version-1 lifecycle policy schema and use its `base_branch` and `feature_branch_prefix`; otherwise use `main` and `feature/`.

Use once, before specification or implementation work that will change `/code/`. This skill owns only safe local branch creation; it does not implement, validate, commit task changes, merge, delete branches, or contact remotes.

1. Confirm `/code/` is a Git worktree, `HEAD` is attached to the policy base branch, that local branch exists, and both the worktree and index are clean. If any condition fails, report the exact blocker and stop. Never checkpoint, stash, reset, restore, clean, or reuse pre-existing work.
2. Derive one Git-valid `<feature_branch_prefix><task-slug>` name from the requested user outcome. The slug must be concise and deterministic.
3. Confirm the branch does not already exist. If it exists, report the name and stop; never reuse, delete, or rename it.
4. Execute `python3 /code/skills/feature-branch-setup/scripts/setup-feature-branch.py --outcome <outcome> [--policy /tmp/opencode/lifecycle-policy.json]`; it performs the checks and creates/switches exactly one unique branch. Never fetch, pull, push, use a remote, or alter the policy base.
5. Report the new feature branch, policy selection, and base revision.
