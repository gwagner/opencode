---
name: github-pr-ready
description: Marks one checked draft pull request ready, or verifies an already-ready pull request, for an exact-head user decision.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-pr-ready/scripts/ready-pr.py *": allow
  external_directory:
    "/code/skills/github-pr-ready/scripts/ready-pr.py": allow
inputs:
  - one open pull request with passed required checks
  - exact expected head branch, head commit, and base branch
  - expected GitHub repository from the current checkout
  - authenticated GitHub CLI
---

# GitHub pull request ready

## Inputs

Require one open pull request with passed required checks, its exact expected head branch, head commit, and base branch, the expected GitHub repository from the current checkout, and an authenticated GitHub CLI.

## Procedure

1. Require canonical passed required-check evidence for the expected head branch and head commit.
2. Run `python3 /code/skills/github-pr-ready/scripts/ready-pr.py --pr <pr> --expected-head <head> --expected-branch <branch> --expected-base <base>`. The script re-reads the canonical checkout-repository pull request immediately before any ready mutation and blocks if its identity changed.
3. Require one versioned JSON result. Accept `ready` or `already-ready` only after every configured `origin` fetch and effective push URL and the non-cross-repository PR head match the checkout repository, and the PR has open non-draft state with unchanged head, head branch, and base.
4. Return `waiting-external` for authentication, network, GitHub availability, or an unconfirmed transition. Return `blocked-unsafe` for malformed output, changed repository identity, changed head or branch, changed base, or an externally completed transition after the ready command failed.

## Boundaries

- Never edit, push, approve, merge, close, or change the pull-request head or base.
- Never mark a pull request ready before required checks pass for its current head.
- GitHub does not expose an expected-head condition for the ready transition; minimize that non-atomic window with immediate before-and-after identity checks and invalidate all prior evidence if either check changes.

## Completion

Report `ready`, `already-ready`, `waiting-external`, or `blocked-unsafe`; repository, pull-request URL, head, base, previous draft state, verified ready state, whether a mutation occurred, and blocker.
