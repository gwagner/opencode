---
name: github-pr-lifecycle-recovery
description: Selects the resumable branch or pull-request state for one CLI- or OpenChamber-originated non-issue lifecycle without mutating it.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.json": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py": allow
inputs:
  - optional `/tmp/opencode/lifecycle-policy.json`
  - provenance: cli or openchamber
  - current non-main branch
  - current OpenChamber-linked worktree for openchamber provenance
  - expected base branch main
  - expected validated local head when resuming an unpublished or published no-PR commit
  - authenticated GitHub CLI
---

# GitHub pull-request lifecycle recovery

## Inputs

Require explicit provenance `cli` or `openchamber`, the current non-`main` branch, expected base branch `main`, and an authenticated GitHub CLI. When resuming any local or remote commit without a pull request, additionally require its expected validated head. OpenChamber provenance additionally requires the current OpenChamber-linked worktree supplied by the caller.

A caller MAY provide `/tmp/opencode/lifecycle-policy.json`; every invocation passes it as `--policy /tmp/opencode/lifecycle-policy.json`. It may change only validated repository-local names, sources, evidence IDs, check/visual allowlists, and delegate hints; exact-head, authenticated-actor, validation, no-auto-merge, manual-method, and fail-closed disambiguation invariants remain mandatory.

## Procedure

All lifecycle scripts import `/code/skills/github_pr_lifecycle_common.py` for fail-closed checkout identity, marker, remote-ref, JSON, and version-1 result-envelope primitives; this skill retains its operation-specific predicates and mutations.

1. Run `python3 /code/skills/github-pr-lifecycle-recovery/scripts/recover-pr.py --provenance <provenance> --base main [--expected-head <head>]`.
2. On `fresh-local`, continue to worktree validation for `openchamber` or ownership baseline for `cli`. For OpenChamber, route `local-commit-no-remote` or `remote-branch-no-pr` through `openchamber-worktree-validation` in `resume-publication` mode before publication; for CLI, continue directly to publication only when caller-supplied retained passed validation and commit evidence names the exact local and remote head. On `open-pull-request`, continue to ownership baseline for `cli` or worktree validation before ownership baseline for `openchamber`, then continue to hosted checks. On `recovered-merged-needs-reattest`, require fresh explicit re-attestation of the exact immutable PR URL, branch, head, base, and claimed manual policy-selected before exact merged-state verification; then resume exact-head leased remote cleanup when needed. Never infer approval, merge method, or actor from merged state.
3. Require every configured Git remote `origin` fetch and effective push URL to match the checkout GitHub repository. Require every matching pull request to be non-cross-repository with its head repository equal to the checkout repository and exactly one matching provenance marker with no issue marker. Accept `local-commit-no-remote` or `remote-branch-no-pr` only for a clean worktree whose local head exactly matches caller-supplied validated-head evidence. Require CLI recovery branches to use the orchestrator-owned `feature/*` namespace. Return `waiting-external` for unavailable remote services, `waiting-user-cleanup` when fresh or open-pull-request work has uncommitted local changes, and `blocked-unsafe` for a base other than `main`, multiple pull requests, closed non-merged matches, changed repository or branch identity, conflicting provenance, any issue marker, ambiguous heads, or unpublished heads without exact retained validation evidence.
4. Never mutate Git or GitHub.

## Completion

Report repository, origin fetch and push identity, branch, local head, remote head, pull request and head repository when present, `fresh-local`, `local-commit-no-remote`, `remote-branch-no-pr`, `open-pull-request`, `waiting-user-cleanup`, `waiting-external`, or `blocked-unsafe`; next stage and blocker.
