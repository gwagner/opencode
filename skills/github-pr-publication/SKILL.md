---
name: github-pr-publication
description: Idempotently publishes one validated committed head to a unique draft pull request for a supported SDLC entry point.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-publication/scripts/publish-pr.py *": allow
  external_directory:
    "/code/skills/github-pr-publication/scripts/publish-pr.py": allow
inputs:
  - provenance: cli, openchamber, or github-issue
  - current non-main branch and expected committed head
  - caller-provided pull-request title and body
  - optional originating issue number required for github-issue provenance
  - authenticated GitHub CLI
---

# GitHub pull-request publication

## Inputs

Require provenance `cli`, `openchamber`, or `github-issue`; the current non-`main` branch and expected committed head; a caller-provided pull-request title and body; an originating issue number exactly when provenance is `github-issue`; and an authenticated GitHub CLI.

## Procedure

1. Run `python3 /code/skills/github-pr-publication/scripts/publish-pr.py --provenance <provenance> --expected-head <head> --title <title> --body <body> [--issue <issue>]`.
2. Require one versioned JSON result. The script treats text as subprocess data, never shell syntax.
3. Accept `created`, `updated`, or `reused` only when exactly one open pull request has the current branch and expected head. The script may recover a remote branch for which PR creation was interrupted.
4. Return `waiting-external` for authentication, network, push, or GitHub availability failures. Return `blocked-unsafe` for dirty state, changed head, a base branch checkout, multiple pull requests, a merged or closed branch match, or provenance mismatch.
5. Never force-push, switch branches, merge, close a pull request, or mutate an issue.

## Completion

Report repository, provenance, branch, published head, pull-request URL, `created`, `updated`, `reused`, `waiting-external`, or `blocked-unsafe`, and evidence.
