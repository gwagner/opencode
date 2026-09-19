---
name: feature-branch-lifecycle
description: Owns the local feature-branch, end-user acceptance, and local-main integration lifecycle for a validated non-loop code change.
---

# Feature branch lifecycle

Use only outside `TODO_LOOP_MODE=true`, for one approved code change that will be implemented by
`code-implementor`. This procedure owns Git lifecycle, not implementation or validation design.

## Before implementation

1. Confirm the repository is Git-controlled, local `main` exists, and the current worktree and
   index are clean. Otherwise report the exact blocker; do not checkpoint, stash, reset, restore,
   or reuse pre-existing work.
2. Derive one Git-valid `feature/<task-slug>` branch name from the requested outcome. If the branch
   already exists, stop and report it rather than reusing or deleting it.
3. Create and switch to that branch directly from local `main`. Never fetch, pull, push, or use a
   remote.

## Iterations and acceptance

1. Before each implementation iteration, `git-auto-commit` establishes its ownership baseline.
2. Each iteration must complete `project-validation`. Commit only when every applicable check
   passed; never commit failed, blocked, or required-but-skipped validation.
3. Ask the end user whether the committed change works as intended.
4. If the answer is no, retain the feature branch and return one focused feedback item to the
   implementation workflow for another iteration. Do not merge.
5. If the answer is yes, continue to local integration.

## Local integration

1. Confirm the accepted iteration is committed and the feature worktree is clean.
2. Load `git-main-sync` to reconcile the feature branch with local `main`. If it reports deferred
   integration, a failed/blocked validation, or an unresolved conflict, do not merge.
3. Confirm `main` remains clean, switch to local `main`, and fast-forward merge the accepted
   feature branch only. Do not create a merge commit or force an integration.
4. Delete the merged local feature branch only after the fast-forward merge succeeds.

## Report

Report feature branch, task commits, acceptance answer, sync status, local-main merge result,
deleted branch status, and every validation result.
