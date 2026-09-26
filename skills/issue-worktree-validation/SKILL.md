---
name: issue-worktree-validation
description: Validates that issue-originated implementation is starting in a clean OpenChamber-owned linked worktree based on local main.
classification: technical
opencode_permission:
  bash:
    "git rev-parse --is-inside-work-tree": allow
    "git rev-parse --show-toplevel": allow
    "git rev-parse --git-dir": allow
    "git rev-parse --git-common-dir": allow
    "git rev-parse HEAD": allow
    "git rev-parse main": allow
    "git branch --show-current": allow
    "git worktree list --porcelain": allow
    "git status --porcelain=v1": allow
inputs:
  - caller-attested OpenChamber issue worktree session
  - attached GitHub issue context
  - expected execution route
  - active implementation agent identity
  - local main as the required starting revision
  - dependency closure evidence when the issue declares dependencies
---

# Issue worktree validation

## Inputs

Require a caller-attested OpenChamber issue worktree session, its attached GitHub issue context, the expected execution route, the active implementation agent identity, local `main` as the required starting revision, and dependency closure evidence when the issue declares dependencies.

## Technology rule

OpenChamber owns physical worktree and session lifecycle. Its documented workflow creates a branch, folder, and session together, while externally removing the folder leaves a worktree needing attention. Validate Git state without running `git worktree add`, `git worktree remove`, `git worktree prune`, moving a worktree, switching branches, or deleting directories. Sources: `https://docs.openchamber.dev/worktrees/` and `https://docs.openchamber.dev/troubleshooting/worktrees-git/`.

## Procedure

1. Require explicit caller attestation that OpenChamber created the current session from the attached GitHub issue with **Create in worktree**. Git metadata alone does not prove OpenChamber ownership. If the attestation or attached issue context is absent, report `blocked` without changing Git state.
2. Run `git rev-parse --is-inside-work-tree` and require `true`. Resolve the current root with `git rev-parse --show-toplevel`.
3. Run `git rev-parse --git-dir` and `git rev-parse --git-common-dir`. Require distinct resolved directories, proving the current checkout is a linked worktree rather than the primary checkout.
4. Run `git worktree list --porcelain`. Require the current root to appear exactly once and reject duplicate, missing, detached, locked, or prunable entries for that root.
5. Run `git branch --show-current`. Require a nonempty branch other than `main`.
6. Run `git status --porcelain=v1`. Require no staged, unstaged, untracked, or conflicted state before implementation begins.
7. Run `git rev-parse HEAD` and `git rev-parse main`. Require identical revisions, proving the fresh issue branch started from current local `main`. Do not fetch, pull, infer a remote base, or repair a mismatch.
8. Read the attached issue context. Require `openchamber:ready`, absence of `openchamber:blocked`, and an `Execution route` equal to the active agent identity. When `Depends on` is present, require caller-provided evidence that every referenced issue is closed; do not contact GitHub or infer dependency state. Treat labels and route as repository conventions, not native OpenChamber dispatch.
9. Return `passed` only when every check succeeds. Otherwise return `blocked` with the failed invariant, observed branch, worktree root, local-main revision when available, and the exact OpenChamber action needed to recreate or correct the session. The caller must stop before baseline capture, synchronization, investigation, or implementation when this result is `blocked`.

## Boundaries

- Never create, remove, prune, move, repair, or switch a worktree or branch.
- Never edit files, implement issue work, contact a remote, or mutate the GitHub issue.
- Never accept the primary checkout, a dirty worktree, a detached branch, a non-`main` base, unresolved dependencies, or the wrong execution route.

## Completion

Report `passed` or `blocked`, current root, branch, HEAD, local-main revision, linked-worktree evidence, clean-state result, issue readiness, route match, and any corrective OpenChamber action.
