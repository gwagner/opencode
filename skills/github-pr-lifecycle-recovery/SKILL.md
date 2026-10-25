---
name: github-pr-lifecycle-recovery
description: Selects the resumable branch or pull-request state for one CLI- or OpenChamber-originated non-issue lifecycle without mutating it.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py *": allow
  external_directory:
    "/code/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py": allow
inputs:
  - provenance: cli or openchamber
  - current non-main branch
  - current OpenChamber-linked worktree for openchamber provenance
  - expected base branch
  - authenticated GitHub CLI
---

# GitHub pull-request lifecycle recovery

## Inputs

Require explicit provenance `cli` or `openchamber`, the current non-`main` branch, the expected base branch, and an authenticated GitHub CLI. OpenChamber provenance additionally requires the current OpenChamber-linked worktree supplied by the caller.

## Procedure

1. Run `python3 /code/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py --provenance <provenance> --base <base>`.
2. On `fresh-local`, continue to worktree validation for `openchamber` or ownership baseline for `cli`. Continue to publication on `remote-branch-no-pr`; continue to hosted checks on `open-pull-request`. Report `merged` when the merged PR's remote branch is absent or `merged-cleanup-pending` when it remains.
3. Require CLI recovery branches to use the orchestrator-owned `feature/*` namespace. Return `waiting-external` for unavailable remote services and `blocked-unsafe` for multiple pull requests, non-open matches, changed branch identity, provenance mismatch, ambiguous heads, or unpublished local commits without durable remote evidence.
4. Never mutate Git or GitHub.

## Completion

Report repository, branch, local head, remote head, pull request when present, `fresh-local`, `remote-branch-no-pr`, `open-pull-request`, `merged`, `merged-cleanup-pending`, `waiting-external`, or `blocked-unsafe`; next stage and blocker.
