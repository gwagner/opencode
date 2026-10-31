---
name: git-change-baseline
description: Records a safe ownership baseline before task-owned editing begins.
classification: technical
opencode_permission:
  bash:
    "python3 /code/skills/git-change-baseline/scripts/capture-baseline.py": allow
  external_directory:
    "/code/skills/git-change-baseline/scripts/capture-baseline.py": allow
inputs:
  - task-change ownership context
  - current Git worktree
---

# Git change baseline

## Inputs

Require the task-change ownership context and current Git worktree.

Use only when the caller or its orchestrator owns the task change and may later receive task-commit authorization, before the first task-owned edit. This skill owns baseline capture only; it does not authorize or perform validation, staging, commit, merge, reset, restore, clean, stash, amend, push, or remote contact.

Run `python3 /code/skills/git-change-baseline/scripts/capture-baseline.py`. It records the attached branch, immutable `HEAD` commit, and every pre-existing change without mutating Git. It blocks if the index is already staged, because staged changes cannot be safely attributed to the new task.

Preserve pre-existing changes as non-task-owned. A continuation with unstaged task-owned changes is valid when the caller supplies that ownership context; do not reject it solely because the worktree is dirty.

## Completion

Report `passed` with the branch, baseline commit, and pre-existing changes, or `blocked` with the exact inspection or staged-change blocker.
