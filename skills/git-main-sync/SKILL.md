---
name: git-main-sync
description: Safely synchronizes a feature branch with local main before code work, checkpointing work and resolving conflicts from evidence.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  bash:
    "git status --porcelain=v1*": allow
    "git rev-parse *": allow
    "git diff *": allow
    "git add -- *": allow
    "git commit -m *": allow
    "git merge --no-commit --no-ff main": allow
    "git merge --abort": allow
  task: allow
inputs:
  - current feature Git worktree
  - local main
---

# Git main sync

## Inputs

Require a current feature Git worktree and local main.

## Deterministic workflow

```yaml
request: "Synchronized feature branch against local main"
workflow:
  - id: "resolve-conflicted-merge"
    when: "When the local-main merge has conflicts."
    agent: "merge-evidence-resolver"
```

Use before editing a code task when the repository is Git-controlled. Never invoke `origin`, any remote, network, SSH, fetch, pull, or push command; this workflow uses local `main` only. Never use on local `main`, a detached HEAD, or a non-Git directory; record `Sync: skipped` and continue without altering it.

1. Record the current branch, `git status --porcelain=v1`, and current `HEAD`. Confirm local `main` is available.
2. If the worktree or index is dirty, record its paths and inspect their diff and non-ignored untracked content. Stage the recorded non-ignored paths explicitly and create a local `sync checkpoint` commit on the current feature branch. This checkpoint preserves existing loop work before integration; it is not a user-requested task commit and must be reported separately. Never reset, restore, clean, stash, amend, or omit a recorded non-ignored path. Ignored files are outside Git merge semantics; report them but never stage them.
3. If clean, start `git merge --no-commit --no-ff main`. If no conflict occurs, inspect `git diff --check` and run the narrowest required project-native validation on the merged tree. Commit the clean merge only after those checks pass.
4. If conflicts occur, record every unmerged path and conflict type. Invoke `merge-evidence-resolver` in this feature worktree and wait for its committed result. The resolver owns evidence gathering, path resolution, merge-caused repairs, validation, and the merge-resolution commit. Do not abort, select a side, switch branches, or modify a conflicted path while it runs.
5. If the resolver cannot complete, preserve the checkpoint and unmerged state, report `Sync: deferred (resolver failed)`, and continue only work that does not alter unresolved paths. Never reset, restore, clean, stash, force-push, or modify unrelated work.
6. If a clean merge's validation fails, cannot run, or its commit fails, run `git merge --abort`, record `Sync: deferred (merge validation)`, and continue the requested task. Never reset, restore, clean, stash, force-push, or modify unrelated work.
7. In the final report, state branch, checkpoint commit when created, pre-merge local `main` revision, `Sync: completed|deferred|skipped`, merge result, validation, merge-resolution commit when created, and unresolved integration status. Say explicitly when no conflicts occurred.

Checkpoint and merge commits are synchronization commits, not part of the task-owned change set. Do not include either in a task commit or claim ownership of pre-existing branch changes. A deferred sync never blocks independent loop work; it must remain visible as integration debt.
