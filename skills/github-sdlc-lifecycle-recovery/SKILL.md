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
  - retained validated head when resuming a remote branch without a pull request
  - authenticated GitHub CLI
---

# GitHub issue lifecycle recovery

## Inputs

Require the originating GitHub issue URL or number, the expected GitHub repository from the current checkout, an optional current branch when an OpenChamber worktree exists and no matching pull request supplies the canonical branch, retained passed validation and commit evidence naming the exact head when that branch exists remotely without a pull request, and an authenticated GitHub CLI.

## Procedure

1. Run `python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py --issue <issue> [--branch <branch>] [--validated-head <head>]`.
2. Require one versioned JSON result. Require every configured Git remote `origin` fetch and effective push URL and the issue URL to belong to the checkout repository. Require every issue-referenced pull request to target `main`; never discard a wrong-base match. Require every matching pull request to be non-cross-repository with its head repository equal to the checkout repository and exactly one matching `OpenCode-Origin:` line and `Refs #` line. GitHub state is authoritative over local state whenever a matching pull request exists. The matching pull request's `headRefName` is the canonical branch; reject a conflicting caller-supplied branch. Without a matching pull request, require the caller-supplied branch to be the current clean local branch and require its local and remote head to equal retained validated-head evidence before resuming publication.
3. Resume only the returned exact next stage. `remote-branch-no-pr` first resumes issue-worktree validation in `resume-publication` mode; `open-pull-request` resumes worktree validation before ownership baseline and hosted checks; `merged-needs-close` resumes issue closure; `closed` is terminal only after verifying the unique merged pull request, absent remote branch, current lifecycle evidence, and exact completion evidence. A recovered merged pull request with a remote branch or without exact completion evidence is `blocked-unsafe`; recovery must not attribute, clean up, or complete a merge lacking durable lifecycle-owned approval and merge evidence.
4. Accept current and completion lifecycle comments only when every lifecycle-controlled prefix occurs exactly once with its required value and the comment was posted by the currently authenticated GitHub actor. Current evidence must contain either exact `Visual evidence: not required` or exact `Visual evidence: passed` plus one uploaded `https://github.com/user-attachments/` Markdown image each with `Before:` and `After:` alt text naming the same scenario. GitHub CLI rewrites body-referenced local attachment paths while preserving alt text as documented at https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli; use that rewritten body as recovery evidence. Accept byte-identical repeated valid evidence, but return `blocked-unsafe` when repeated valid current or completion comments differ. Return `waiting-external` for authentication, network, or GitHub availability. Return `waiting-user-cleanup` for a dirty no-PR recovery worktree. Return `blocked-unsafe` for malformed comment shapes, multiple matches, conflicting markers or identifiers, wrong-base matches, malformed states, externally attributable merges, or retained-evidence ambiguity.

## Boundaries

- Never mutate GitHub, Git, branches, or worktrees.
- Never infer a pull request from a title alone.

## Completion

Report repository, origin fetch and push identity, authenticated actor, issue, canonical branch, matching PR and head repository, head, verified merge commit, remote-branch state, cleanup disposition when verified, lifecycle disposition, exact next stage, evidence, and blocker.
