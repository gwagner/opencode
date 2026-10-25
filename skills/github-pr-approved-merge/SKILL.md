---
name: github-pr-approved-merge
description: Verifies that a user manually squash-merged one exact approved GitHub pull request without performing the merge.
classification: technical
opencode_permission:
  question: allow
  shell:
    "python3 /code/skills/github-pr-check-validation/scripts/validate-checks.py *": allow
    "python3 /code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-pr-check-validation/scripts/validate-checks.py": allow
    "/code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py": allow
  skill:
    github-pr-check-validation: allow
inputs:
  - resolved `/tmp/opencode/lifecycle-policy.snapshot.json` and its expected digest
  - one open approved pull request or one recovered merged pull request targeting main
  - explicit current-turn approval and separate confirmation, or recovered exact-identity manual-method re-attestation
  - user available to perform and confirm the manual policy-selected when the pull request is open
  - expected GitHub repository from the current checkout
  - authenticated GitHub CLI
---

# GitHub approved manual-merge verification

## Inputs

Require either one open GitHub pull request targeting `main` with explicit user approval and separate manual-merge confirmation, or one recovered merged pull request with fresh explicit re-attestation of the exact immutable PR URL, head branch, head commit, base, and claimed manual policy-selected. Also require the expected checkout repository and authenticated GitHub CLI.

## Workflow

```yaml
request: "One exact user-approved pull request verified after manual policy-selected merge."
workflow:
  - id: required-check-recheck
    when: "The open pull request, approved head branch, head commit, and base branch passed the initial merge gate."
    skill: github-pr-check-validation
  - id: manual-method-merge
    when: "The exact open pull request passed the immediate required-check recheck."
    ask: "Manually squash-merge this exact pull request in GitHub, then confirm completion for this unchanged head branch and head commit."
```

The orchestrator first resolves the caller source into `/tmp/opencode/lifecycle-policy.snapshot.json`; every invocation passes that snapshot as `--policy /tmp/opencode/lifecycle-policy.snapshot.json --expected-policy-digest <digest>` and never reuses the source. It may change only validated repository-local names, sources, evidence IDs, check/visual allowlists, and delegate hints; exact-head, authenticated-actor, validation, no-auto-merge, manual-method, and fail-closed disambiguation invariants remain mandatory.

## Procedure

All lifecycle scripts import `/code/skills/github_pr_lifecycle_common.py` for fail-closed checkout identity, marker, remote-ref, JSON, and version-1 result-envelope primitives; this skill retains its operation-specific predicates and mutations.

1. Before asking the user to merge, require open state, base `main`, mergeable status, ready state, and an exact match between the current head branch, head commit, and current-turn user decision context.
2. Invoke `github-pr-check-validation` immediately before requesting the manual policy-selected merge, supplying this exact current head. Require its `passed` result.
3. Ask the user to manually squash-merge that exact pull request in GitHub and confirm completion. Never treat silence, approval alone, or an ambiguous response as confirmation.
4. Only after current-turn confirmation or recovered-merge re-attestation, run `python3 /code/skills/github-pr-approved-merge/scripts/merge-approved-pr.py --pr <pr> --expected-head <approved head> --expected-branch <approved branch> --expected-base main --confirmed-manual-method`. For recovered merged state, the pre-merge check stage is not replayable; require retained exact-head check evidence when applicable and treat re-attestation as a recovery act, never retroactive approval.
5. Require one versioned JSON result. Require every configured `origin` fetch and effective push URL and the non-cross-repository pull-request head to match the checkout GitHub repository. The script performs no merge or other mutation.
6. Boundedly re-read after confirmation. Return `waiting-external` when GitHub reports temporary or `UNKNOWN` mergeability through the bound, `blocked-unsafe` for a confirmed conflict or identity change, and `waiting-user-merge` with continuation `manual-merge-verification` when the exact pull request remains open and unchanged. Accept `user-merged` only when GitHub reports merged state, unchanged head, head branch, and base, plus a merged timestamp and merge commit.

## Boundaries

- Never parse or classify required checks outside `github-pr-check-validation`; never bypass its result or infer approval or merge completion.
- Never run `gh pr merge`, a merge API mutation, or any automatic merge. The user owns the manual policy-selected merge; this skill only verifies the exact resulting GitHub state.
- Never delete a local or remote branch, worktree, or directory. Remote branch cleanup belongs to `github-pr-remote-branch-cleanup`.

## Completion

Report `user-merged`, `waiting-user-merge`, `waiting-external`, or `blocked-unsafe`; repository, pull-request URL, approved head and base branch, canonical required-check result, explicit user attestation, exact merged-state verification, and blocker. State that GitHub technically proves only the exact PR's merged state after attestation; it does not prove merge method or actor.
