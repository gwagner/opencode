---
name: merge-conflict-resolution
description: Resolves merge conflicts on a named local branch, merges that branch into local main, and deletes the merged branch. Use only when the user explicitly requests this complete Git workflow.
---

# Merge conflict resolution

Perform the requested integration locally. Resolve conflicts on the source branch before advancing `main`. Proceed only when the user explicitly requested this workflow; create no commits except those needed for that request. Do not fetch, pull, push, delete a remote branch, or open a pull request unless explicitly requested.

## Safety gates

1. Identify the exact source branch. Never infer it when multiple branches are plausible. Reject `main` as the source.
2. Confirm the current directory is the intended Git worktree, local `main` and the source branch exist, and no merge, rebase, cherry-pick, or revert is already in progress.
3. Require a clean index and worktree, including untracked files. Never stash, reset, restore, clean, overwrite, or include pre-existing work to make the tree clean. Stop and report existing changes.
4. Inspect repository guidance, relevant history, and worktrees. Inspect upstreams only when remote state matters. Stop if either branch is checked out in another worktree or repository policy requires a pull request instead of a local merge.
5. Record the starting object IDs of `main` and the source branch. Use local `main` as requested; do not silently substitute a remote-tracking branch.

## Integrate `main` on the source branch

1. Switch to the source branch and run `git merge --no-commit main`. Do not rebase, squash, or force-update history unless the user explicitly requested that strategy. Note that Git cannot pause a fast-forward merge; inspect and validate that resulting tree before continuing.
2. If the merge is clean, continue. If it conflicts:
   - List every unmerged path and classify content, rename, delete/modify, binary, submodule, and mode conflicts.
   - For each path, inspect the base, source-branch side, `main` side, nearby history, callers, tests, and authoritative requirements when relevant. During this merge, `ours` is the source branch and `theirs` is `main`.
   - Preserve both intended behaviors when compatible. Never choose all `ours` or all `theirs` merely to finish, and never invent product behavior.
   - Ask the user and leave the conflict safely in progress when intent remains materially ambiguous. Report the exact paths and decision needed.
   - Stage only deliberately resolved paths. Confirm no unmerged entries or conflict markers remain and run `git diff --check` before completing the merge commit.
3. Inspect the full resulting diff and commit graph. Ensure the merge contains only source work, updates from `main`, and deliberate resolutions.
4. Load and follow `project-validation` on the resolved source branch. Do not complete the workflow if required validation fails.
5. Complete the merge commit when Git has not already done so. Do not amend unrelated commits.

## Advance `main` and remove the source branch

1. Recheck that the worktree is clean and local `main` still points to its recorded starting object. If `main` moved, stop and report that the updated `main` must be integrated and validated before retrying.
2. Record the validated source tip object ID, switch to `main`, and merge that immutable object with `git merge --ff-only <validated-source-oid>`. A fast-forward should be possible because the recorded `main` was merged into the source. If it is not, stop rather than creating or resolving new conflicts on `main`.
3. Verify `main` equals the validated source tip, the source tip is an ancestor of `main`, required checks passed for that exact tree, and the worktree is clean.
4. Confirm the source branch still points to the validated object ID. Then delete it with safe deletion (`git branch -d <source>`), never force deletion. If its ref moved or deletion is refused, retain it and report why.

## Failure handling and report

- If a command fails before `main` advances, preserve the source branch and current diagnostic state. Abort a merge only when doing so cannot discard user work and retaining it provides no value.
- If validation fails, do not merge into `main` or delete the source branch.
- If failure occurs after `main` advances, never rewrite or reset `main`; retain the source branch and report the exact recovery state.
- Report source branch, starting and final object IDs, conflict files and resolution rationale, validation commands and results, merge strategy, local/remote deletion status, and blockers.
