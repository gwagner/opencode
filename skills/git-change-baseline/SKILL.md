---
name: git-change-baseline
description: Records a safe ownership baseline for one authorized future task commit before editing begins.
---

# Git change baseline

Use only when a task commit is authorized, before the first edit. This skill owns baseline capture only; it does not validate, stage, commit, merge, reset, restore, clean, stash, amend, push, or contact a remote.

1. Record `git status --porcelain=v1 -z` and require an empty index.
2. Record every pre-existing worktree path. Preserve and exclude those paths from the later task commit.
3. Report the baseline result for `git-auto-commit`.
