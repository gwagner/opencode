---
name: execution-evidence-reporting
description: Returns one standardized execution-evidence record for a bounded code-editing specialist result.
classification: technical
opencode_permission:
  bash:
    "git status --porcelain=v1 -z": allow
    "git diff -- *": allow
inputs:
  - current Git worktree
  - caller-provided owned changed paths
  - project-validation state, commands, and material results
  - baseline evidence when captured
  - decisions, assumptions, unresolved questions, and blockers
---

# Execution evidence reporting

## Inputs

Require the current Git worktree, caller-provided owned changed paths, project-validation state with exact commands and material results, baseline evidence when captured, and any decisions, assumptions, unresolved questions, and blockers.

## Procedure

1. Run `git status --porcelain=v1 -z` and `git diff -- <owned-path>` for every caller-provided owned changed path. Do not stage, commit, restore, clean, switch, create, remove, or otherwise alter the worktree.
2. Reconcile the observed paths with the supplied ownership and baseline evidence. Report paths that are pre-existing, unowned, or not represented by the supplied baseline as blockers.
3. Return exactly these fields: outcome; owned changed paths; project-validation state (`passed`, `failed`, `skipped`, or `blocked`); exact project-validation commands and material results; decisions; assumptions; unresolved questions; blockers; and baseline.

## Completion

This skill reports evidence only. It does not replace project validation, authorize delivery, or perform any local or remote Git lifecycle action.
