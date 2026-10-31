---
name: git-change-baseline
description: Records a safe ownership baseline before task-owned editing begins.
classification: technical
opencode_permission:
  bash:
    "git status --porcelain=v1 -z": allow
    "git branch --show-current": allow
    "git rev-parse --verify HEAD": allow
inputs:
  - task-change ownership context
  - current Git worktree
---

# Git change baseline

## Inputs

Require the task-change ownership context and current Git worktree.

Use only when the caller or its orchestrator owns the task change and may later receive task-commit authorization, before the first task-owned edit. This skill owns baseline capture only; it does not authorize or perform validation, staging, commit, merge, reset, restore, clean, stash, amend, push, or remote contact.

1. Record the branch with `git branch --show-current`, the immutable baseline commit with `git rev-parse --verify HEAD`, then record `git status --porcelain=v1 -z` and require an empty index. Preserve all three values in the later commit decision evidence.
2. Record every pre-existing worktree path. Preserve and exclude those paths from the later task commit.
3. Report the baseline result for a later `git-delegated-change-commit` invocation.
