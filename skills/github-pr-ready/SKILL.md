---
name: github-pr-ready
description: Marks one checked draft pull request ready, or verifies an already-ready pull request, for an exact-head user decision.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-ready/scripts/ready-pr.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-pr-ready/scripts/ready-pr.py": allow
inputs:
  - resolved `/tmp/opencode/lifecycle-policy.snapshot.json` and its expected digest
  - one open pull request with passed required checks
  - exact expected head branch, head commit, and base branch
  - expected GitHub repository from the current checkout
  - authenticated GitHub CLI
---

# GitHub pull request ready

## Inputs

Require one open pull request with passed required checks, its exact expected head branch, head commit, and base branch, the expected GitHub repository from the current checkout, and an authenticated GitHub CLI.

The orchestrator first resolves the caller source into `/tmp/opencode/lifecycle-policy.snapshot.json`; every invocation passes that snapshot as `--policy /tmp/opencode/lifecycle-policy.snapshot.json --expected-policy-digest <digest>` and never reuses the source. It may change only validated repository-local names, sources, evidence IDs, check/visual allowlists, and delegate hints; exact-head, authenticated-actor, validation, no-auto-merge, manual-method, and fail-closed disambiguation invariants remain mandatory.

## Procedure

All lifecycle scripts import `/code/skills/github_pr_lifecycle_common.py` for fail-closed checkout identity, marker, remote-ref, JSON, and version-1 result-envelope primitives; this skill retains its operation-specific predicates and mutations.

1. Require canonical passed required-check evidence for the expected head branch and head commit.
2. Run `python3 /code/skills/github-pr-ready/scripts/ready-pr.py --pr <pr> --expected-head <head> --expected-branch <branch> --expected-base <base>`. The script re-reads the canonical checkout-repository pull request immediately before any ready mutation and blocks if its identity changed.
3. Require one versioned JSON result. Accept `ready` or `already-ready` only after every configured `origin` fetch and effective push URL and the non-cross-repository PR head match the checkout repository, and the PR has open non-draft state with unchanged head, head branch, and base.
4. Return `waiting-external` for authentication, network, GitHub availability, or an unconfirmed transition. Return `blocked-unsafe` for malformed output, changed repository identity, changed head or branch, or changed base. If the ready command fails but authoritative inspection proves the exact unchanged PR is ready, accept `ready` with mutation attribution `uncertain`.

## Boundaries

- Never edit, push, approve, merge, close, or change the pull-request head or base.
- Never mark a pull request ready before required checks pass for its current head.
- GitHub does not expose an expected-head condition for the ready transition; minimize that non-atomic window with immediate before-and-after identity checks and invalidate all prior evidence if either check changes.

## Completion

Report `ready`, `already-ready`, `waiting-external`, or `blocked-unsafe`; repository, pull-request URL, head, base, previous draft state, verified ready state, whether a mutation occurred, and blocker.
