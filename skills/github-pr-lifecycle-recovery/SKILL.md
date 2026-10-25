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
  - expected validated local head when resuming an unpublished commit
  - authenticated GitHub CLI
---

# GitHub pull-request lifecycle recovery

## Inputs

Require explicit provenance `cli` or `openchamber`, the current non-`main` branch, the expected base branch, and an authenticated GitHub CLI. Only when resuming an unpublished local commit, additionally require its expected validated head. OpenChamber provenance additionally requires the current OpenChamber-linked worktree supplied by the caller.

## Procedure

1. Run `python3 /code/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py --provenance <provenance> --base <base> [--expected-head <head>]`.
2. On `fresh-local`, continue to worktree validation for `openchamber` or ownership baseline for `cli`. Continue to publication on `local-commit-no-remote` or `remote-branch-no-pr`; continue to hosted checks on `open-pull-request`; continue to remote cleanup on `merged-needs-cleanup`. Report `merged` only when the merged PR's remote branch is absent.
3. Accept `local-commit-no-remote` only for a clean worktree whose local head exactly matches caller-supplied validated-head evidence. Require CLI recovery branches to use the orchestrator-owned `feature/*` namespace. Return `waiting-external` for unavailable remote services, `waiting-user-cleanup` for uncommitted local changes, and `blocked-unsafe` for multiple pull requests, non-open matches, changed branch identity, provenance mismatch, ambiguous heads, or unpublished local commits without exact expected-head evidence.
4. Never mutate Git or GitHub.

## Completion

Report repository, branch, local head, remote head, pull request when present, `fresh-local`, `local-commit-no-remote`, `remote-branch-no-pr`, `open-pull-request`, `merged`, `merged-needs-cleanup`, `waiting-user-cleanup`, `waiting-external`, or `blocked-unsafe`; next stage and blocker.
