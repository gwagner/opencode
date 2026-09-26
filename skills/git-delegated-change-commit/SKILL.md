---
name: git-delegated-change-commit
description: Reviews and commits one validated delegate-owned change batch from an established clean ownership baseline.
classification: technical
opencode_permission:
  read: allow
  bash:
    "git status*": allow
    "git diff*": allow
    "git add -- *": allow
    "git commit --only *": allow
inputs:
  - explicit task-commit authorization
  - clean ownership baseline captured before delegation
  - one completed delegate change batch and owned paths
  - passed delegate project-validation result
  - caller-permitted changed paths
---

# Git delegated change commit

## Inputs

Require explicit task-commit authorization, a clean ownership baseline captured before delegation, one completed delegate change batch with owned paths, its passed `project-validation` result, and caller-permitted changed paths.

## Procedure

1. Run `git status --porcelain=v1 -z` and compare every changed path with the baseline and delegate-owned path report. Stop on staged changes, ownership ambiguity, or an unrelated path.
2. Review `git diff -- <owned paths>` and require the change to match the approved issue scope and delegate report. Never repair or extend the implementation in this skill.
3. Require the delegate's final `project-validation` status to be `passed`; reject failed, skipped, blocked, stale, or missing evidence.
4. Stage only the reviewed paths with `git add -- <owned paths>` and create one descriptive commit with `git commit --only ... -- <owned paths>`.
5. Re-run status and report any remaining change. A later independently validated delegate batch may invoke this skill again as a separate workflow pass.

## Boundaries

- Never commit pre-existing, unreviewed, unvalidated, or ambiguously owned changes.
- Never amend, reset, restore, clean, stash, merge, push, or contact a remote.

## Completion

Report the commit hash, committed paths, delegate validation evidence, remaining status, and blockers.
