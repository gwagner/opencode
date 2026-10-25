---
name: github-pr-check-validation
description: Deterministically classifies and boundedly rechecks required checks for one unchanged open pull request.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-check-validation/scripts/validate-checks.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.*.snapshot.json": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-pr-check-validation/scripts/validate-checks.py": allow
inputs:
  - resolved `/tmp/opencode/lifecycle-policy.<repository-hash>.<lifecycle-run>.snapshot.json` and its expected digest
  - one open GitHub pull request
  - expected pull-request head commit
  - expected GitHub repository from the current checkout
  - authenticated GitHub CLI
  - bounded recheck count and interval
---

# GitHub pull-request check validation

## Inputs

Require one open GitHub pull request, its expected head commit, the expected GitHub repository from the current checkout, an authenticated GitHub CLI, and a bounded recheck count and interval.

The orchestrator first resolves the caller source into `/tmp/opencode/lifecycle-policy.<repository-hash>.<lifecycle-run>.snapshot.json`; every invocation passes that snapshot as `--policy /tmp/opencode/lifecycle-policy.<repository-hash>.<lifecycle-run>.snapshot.json --expected-policy-digest <digest> --repository <owner/name> --lifecycle-run <run-id>` and never reuses the source. It may change only validated repository-local names, sources, evidence IDs, check/visual allowlists, and delegate hints; exact-head, authenticated-actor, validation, no-auto-merge, manual-method, and fail-closed disambiguation invariants remain mandatory.

## Procedure

All lifecycle scripts import `/code/skills/github_pr_lifecycle_common.py` for fail-closed checkout identity, marker, remote-ref, JSON, and version-1 result-envelope primitives; this skill retains its operation-specific predicates and mutations.

1. Run `python3 /code/skills/github-pr-check-validation/scripts/validate-checks.py --pr <pr> --expected-head <head> --max-rechecks <count> --wait-seconds <seconds>`.
2. Require one versioned JSON result with checkout-repository identity, all observed required-check records, and unchanged-head evidence. Require every configured `origin` fetch and effective push URL and the non-cross-repository pull-request head to match that repository before accepting check evidence.
3. Accept `passed` only for verified passing required checks or verified absence of configured required checks.
4. Return `repair-needed` for semantic terminal required-check failures, `waiting-external` for pending deadline or transient CLI, API, transport, authentication, or GitHub unavailability, and `blocked-unsafe` for malformed successful output, changed identity, changed head, invalid recheck bounds, or ambiguous zero-check configuration. A passed result continues to `pull-request-ready`.

## Boundaries

- This skill is the sole owner of required-check parsing, classification, zero-configuration verification, and bounded pending rechecks.
- Never edit code, push, approve, merge, mutate issues, or infer hosted evidence from local validation.

## Completion

Report `passed`, `repair-needed`, `waiting-external`, or `blocked-unsafe`; repository, PR, head, base, attempts, check records, configuration evidence, and blocker.
