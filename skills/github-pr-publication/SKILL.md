---
name: github-pr-publication
description: Idempotently publishes one validated committed head to a unique draft pull request for a supported SDLC entry point.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-publication/scripts/publish-pr.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-pr-publication/scripts/publish-pr.py": allow
inputs:
  - resolved `/tmp/opencode/lifecycle-policy.snapshot.json` and its expected digest
  - provenance: cli, openchamber, or github-issue
  - current non-main branch and expected committed head
  - retained passed project-validation and commit evidence for that exact head
  - caller-provided pull-request title and body
  - optional originating issue number required for github-issue provenance
  - authenticated GitHub CLI
---

# GitHub pull-request publication

## Inputs

Require provenance `cli`, `openchamber`, or `github-issue`; the current non-`main` branch and expected committed head; retained passed `project-validation` and commit evidence naming that exact head; a caller-provided pull-request title and body; an originating issue number exactly when provenance is `github-issue`; and an authenticated GitHub CLI.

The orchestrator first resolves the caller source into `/tmp/opencode/lifecycle-policy.snapshot.json`; every invocation passes that snapshot as `--policy /tmp/opencode/lifecycle-policy.snapshot.json --expected-policy-digest <digest>` and never reuses the source. It may change only validated repository-local names, sources, evidence IDs, check/visual allowlists, and delegate hints; exact-head, authenticated-actor, validation, no-auto-merge, manual-method, and fail-closed disambiguation invariants remain mandatory.

## Procedure

All lifecycle scripts import `/code/skills/github_pr_lifecycle_common.py` for fail-closed checkout identity, marker, remote-ref, JSON, and version-1 result-envelope primitives; this skill retains its operation-specific predicates and mutations.

1. Run `python3 /code/skills/github-pr-publication/scripts/publish-pr.py --provenance <provenance> --expected-head <head> --validated-head <validated head> --title <title> --body <body> [--issue <issue>]`.
2. Require one versioned JSON result. The script treats text as subprocess data, never shell syntax.
3. Reject caller-provided body lines beginning `OpenCode-Origin:` or `Refs #`; the script exclusively appends exactly one canonical provenance marker and, only for issue provenance, exactly one canonical issue marker. Before pushing, require every configured `origin` fetch and effective push URL to match the checkout GitHub repository. Require any reused pull request to be open, non-cross-repository, in that repository, and at the exact branch, base, and exclusive marker identity.
4. Push only the validated commit through an explicit `<head>:refs/heads/<branch>` refspec. Re-read local and remote identity before creating or accepting a pull request.
5. Accept `created`, `updated`, or `reused` only when exactly one open non-cross-repository pull request has the current branch and validated head. The script may recover a validated remote branch for which PR creation was interrupted.
6. After a failed or uncertain push or PR-create command, inspect the exact remote ref and matching PR authoritatively. Accept the exact unchanged branch/head PR with mutation attribution `uncertain`; return resumable `waiting-external` with `pr-publication` when the exact remote head exists but no PR is visible. Return `waiting-external` for other transient authentication, network, push, or GitHub availability failures. Return `blocked-unsafe` for missing validation evidence, dirty state, changed head, a base branch checkout, repository mismatch, cross-repository identity, multiple pull requests, a merged or closed branch match, changed base, or provenance mismatch.
7. Never force-push, switch branches, merge, close a pull request, or mutate an issue.

## Completion

Report repository, provenance, branch, published head, pull-request URL, `created`, `updated`, `reused`, `waiting-external`, or `blocked-unsafe`, and evidence.
