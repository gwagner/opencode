---
name: github-sdlc-lifecycle-recovery
description: Selects the safe resumable state for an issue-originated pull-request lifecycle without mutating it.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py *": allow
  external_directory:
    "/code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py": allow
inputs:
  - originating GitHub issue URL or number
  - expected GitHub repository from the current checkout
  - optional current branch when an OpenChamber worktree exists and no matching pull request supplies the canonical branch
  - authenticated GitHub CLI
---

# GitHub issue lifecycle recovery

## Inputs

Require the originating GitHub issue URL or number, the expected GitHub repository from the current checkout, an optional current branch when an OpenChamber worktree exists and no matching pull request supplies the canonical branch, and an authenticated GitHub CLI.

## Procedure

1. Run `python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py --issue <issue> [--branch <branch>]`.
2. Require one versioned JSON result. GitHub state is authoritative over local state whenever a matching pull request exists. The matching pull request's `headRefName` is the canonical branch; reject a conflicting caller-supplied branch.
3. Resume only the returned exact next stage. `remote-branch-no-pr` resumes publication; `open-pull-request` resumes hosted checks; `merged-needs-cleanup` resumes remote branch cleanup; `merged-needs-completion` resumes completion evidence only with verified `cleanup_disposition: already-absent`; `merged-needs-close` resumes issue closure; `closed` is terminal.
4. Return `waiting-external` for authentication, network, or GitHub availability. Return `blocked-unsafe` for multiple matches, conflicting identifiers, malformed states, or retained-evidence ambiguity.

## Boundaries

- Never mutate GitHub, Git, branches, or worktrees.
- Never infer a pull request from a title alone.

## Completion

Report repository, issue, canonical branch, matching PR, head, merge commit, remote-branch state, cleanup disposition when verified, lifecycle disposition, exact next stage, evidence, and blocker.
