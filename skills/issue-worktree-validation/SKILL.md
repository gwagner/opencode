---
name: issue-worktree-validation
description: Validates and, only when safe, fast-forwards a clean issue worktree to refreshed origin/main before implementation.
classification: technical
opencode_permission:
  bash:
    "git rev-parse --is-inside-work-tree": allow
    "git rev-parse --show-toplevel": allow
    "git rev-parse --git-dir": allow
    "git rev-parse --git-common-dir": allow
    "git rev-parse HEAD": allow
    "git fetch origin main": allow
    "git rev-parse origin/main": allow
    "git merge-base --is-ancestor HEAD origin/main": allow
    "git merge --ff-only origin/main": allow
    "git branch --show-current": allow
    "git worktree list --porcelain": allow
    "git status --porcelain=v1": allow
inputs:
  - attached GitHub issue context
  - lifecycle-recovery disposition reporting no matching pull request
  - expected execution route
  - active implementation agent identity
  - refreshed origin/main as the required delivery revision
  - dependency closure evidence when the issue declares dependencies
---

# Issue worktree validation

## Inputs

Require the attached GitHub issue context, a lifecycle-recovery disposition reporting no matching pull request, the expected execution route, the active implementation agent identity, refreshed `origin/main` as the required delivery revision, and dependency closure evidence when the issue declares dependencies.

## Technology rule

OpenChamber owns physical worktree and session lifecycle. Its documented workflow creates a branch, folder, and session together, while externally removing the folder leaves a worktree needing attention. Validate Git state without running `git worktree add`, `git worktree remove`, `git worktree prune`, moving a worktree, switching branches, or deleting directories. Sources: `https://docs.openchamber.dev/worktrees/` and `https://docs.openchamber.dev/troubleshooting/worktrees-git/`.

The linked-worktree topology, clean state, refreshed `origin/main` equality or safe fast-forward, and ready issue checks in this procedure are sufficient alternate safety evidence to begin implementation. They establish current-worktree eligibility, not OpenChamber lifecycle provenance; Git metadata does not prove how the session was created. Do not request or block on provenance evidence that is not machine-verifiable.

## Procedure

1. Require lifecycle recovery to report the unique no-pull-request fresh-start state. Otherwise stop: GitHub lifecycle state is authoritative and this local-worktree procedure is not applicable.
2. Run `git rev-parse --is-inside-work-tree` and require `true`. Resolve the current root with `git rev-parse --show-toplevel`.
3. Run `git rev-parse --git-dir` and `git rev-parse --git-common-dir`. Require distinct resolved directories, proving the current checkout is a linked worktree rather than the primary checkout.
4. Run `git worktree list --porcelain`. Require the current root to appear exactly once and reject duplicate, missing, detached, locked, or prunable entries for that root.
5. Run `git branch --show-current`. Require a nonempty branch other than `main`.
6. Run `git status --porcelain=v1`. Require no staged, unstaged, untracked, or conflicted state before implementation begins. On any nonempty result, report `blocked` with the exact status and HEAD; do not fetch or synchronize. Tell the user to preserve or discard the user-owned changes before recreating the issue worktree, and retain the status and HEAD as recovery evidence.
7. Read the attached issue context. Require `openchamber:ready`, absence of `openchamber:blocked`, and an `Execution route` equal to the active agent identity. When `Depends on` is present, require caller-provided evidence that every referenced issue is closed; do not contact GitHub or infer dependency state. Treat labels and route as repository conventions, not native OpenChamber dispatch.
8. Run `git fetch origin main`, then resolve `git rev-parse HEAD` and `git rev-parse origin/main`. If they are identical, retain the verified clean state and continue. If they differ, run `git merge-base --is-ancestor HEAD origin/main`. Only when it succeeds may the clean eligible issue branch be updated with `git merge --ff-only origin/main`. Then rerun `git status --porcelain=v1`, `git rev-parse HEAD`, and `git rev-parse origin/main`; require clean status and identical revisions. This is the only permitted synchronization: it neither switches nor merges divergent history.
9. If the ancestor check fails, the fast-forward fails, the post-fast-forward status is dirty, or either revision cannot be resolved, report `blocked`. Preserve and report the pre-sync HEAD, refreshed remote-main revision when available, ancestor-check or fast-forward exit result, post-sync HEAD when available, and clean-state result. Do not infer a base, reset, rebase, merge non-fast-forward history, or repair the branch. Tell the user to recreate the issue worktree from the named refreshed remote-main revision; for a dirty branch, preserve or discard the user-owned changes before recreation, and for divergent history, preserve the branch as recovery evidence.
10. Return `passed` only when every check succeeds. Otherwise return `blocked` with the failed invariant, observed branch, worktree root, refreshed remote-main revision when available, and the exact OpenChamber action needed to recreate or correct the session. The caller must stop before baseline capture, investigation, or implementation when this result is `blocked`.

## Boundaries

- Never create, remove, prune, move, repair, or switch a worktree or branch.
- Never edit files, implement issue work, or mutate the GitHub issue.
- Never accept the primary checkout, a dirty worktree, a detached branch, a branch that is ahead of or divergent from refreshed `origin/main`, unresolved dependencies, or the wrong execution route.

## Completion

Report `passed` or `blocked`, current root, branch, pre-sync HEAD, post-sync HEAD, refreshed remote-main revision, linked-worktree evidence, clean-state result, ancestor-check and fast-forward results when attempted, issue readiness, route match, and any corrective OpenChamber action.
