---
name: github-pr-ready
description: Marks one checked draft pull request ready, or verifies an already-ready pull request, for an exact-head user decision.
classification: technical
opencode_permission:
  shell:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh pr view * --json number,url,state,isDraft,baseRefName,headRefName,headRefOid": allow
    "gh pr ready *": allow
inputs:
  - one open pull request with passed required checks
  - exact expected head and base branch
  - authenticated GitHub CLI
---

# GitHub pull request ready

## Inputs

Require one open pull request with passed required checks, its exact expected head and base branch, and an authenticated GitHub CLI.

## Procedure

1. Run `gh auth status`, `gh repo view --json nameWithOwner,url`, and `gh pr view <pr> --json number,url,state,isDraft,baseRefName,headRefName,headRefOid`.
2. Require open state, the expected head and base, a nonempty head branch, and passed required-check evidence for that same head.
3. If `isDraft` is true, run `gh pr ready <pr>` once. If it is already false, perform no mutation.
4. Re-read the pull request and require open state, `isDraft` false, and unchanged head, head branch, and base.
5. Return `waiting-external` for authentication, network, or GitHub availability failures. Return `blocked-unsafe` for malformed output, changed identity, changed head, or a failed ready transition.

## Boundaries

- Never edit, push, approve, merge, close, or change the pull-request head or base.
- Never mark a pull request ready before required checks pass for its current head.

## Completion

Report `ready`, `waiting-external`, or `blocked-unsafe`; repository, pull-request URL, head, base, previous draft state, verified ready state, whether a mutation occurred, and blocker.
