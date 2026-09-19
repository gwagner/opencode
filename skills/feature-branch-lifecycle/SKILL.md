---
name: feature-branch-lifecycle
description: Owns the local feature-branch, end-user acceptance, and local-main integration lifecycle for a validated non-loop code change.
---

# Feature branch lifecycle

Use only outside `TODO_LOOP_MODE=true`, for one approved, already-created feature branch whose
change will be implemented by `code-implementor`. This procedure owns acceptance and optional
local integration, not branch setup, implementation, or validation design.

## Before implementation

1. Confirm the current branch is the caller-created feature branch, local `main` exists, and the
   branch was created using `feature-branch-setup`. Otherwise report the exact blocker; do not
   checkpoint, stash, reset, restore, clean, or reuse pre-existing work.

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
