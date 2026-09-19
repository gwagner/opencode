---
name: git-main-sync
description: Safely merges local main into a clean current feature branch before code work, resolving only unambiguous non-destructive conflicts and reporting every merge decision.
---

# Git main sync

Use before investigating or editing a code task when the repository is Git-controlled. Never invoke `origin`, any remote, network, SSH, fetch, pull, or push command; this workflow uses local `main` only. Never use on `main`, a detached HEAD, a non-Git directory, or a worktree with pre-existing staged or unstaged changes; report the condition and do not alter it.

1. Record the current branch, `git status --porcelain=v1`, and the current `HEAD`. Confirm local `main` is available.
2. Start `git merge --no-commit --no-ff main`. If no conflict occurs, inspect `git diff --check`, commit the merge only when clean, and continue.
3. If conflicts occur, list every unmerged path and inspect the base, current-branch, and `main` versions. Resolve a path only when the resolution is mechanical and preserves both independently compatible changes (for example, non-overlapping additions). Do not choose a side, delete behavior, rewrite generated or lock files, or invent semantic behavior to force a merge.
4. For each attempted resolution, record: path, conflict type, evidence considered, exact preservation decision, and reason it is non-destructive. Run `git diff --check` and applicable focused validation before committing a resolved merge.
5. If any conflict is ambiguous, validation fails, or the merge cannot be committed, run `git merge --abort`. Do not reset, restore, clean, stash, force-push, or modify unrelated work. Report the blocker and all recorded merge decisions; do not begin the requested code work.
6. In the final report, state branch, pre-merge and merged local `main` revisions, merge result, validation, and a `Merge decisions` list. Say explicitly when no conflicts or resolution decisions occurred.

The merge commit is a synchronization commit, not part of the task-owned change set. Do not include it in a task commit or claim ownership of pre-existing branch changes.
