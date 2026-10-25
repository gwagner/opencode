---
name: github-sdlc-lifecycle-recovery
description: Selects the safe resumable state for an issue-originated pull-request lifecycle without mutating it.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
    "/code/skills/github_issue_comment_common.py": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py": allow
inputs:
  - resolved `/tmp/opencode/lifecycle-policy.snapshot.json` and its expected digest
  - originating GitHub issue URL or number
  - expected GitHub repository from the current checkout
  - optional current branch when an OpenChamber worktree exists and no matching pull request supplies the canonical branch
  - retained validated head when resuming a remote branch without a pull request
  - authenticated GitHub CLI
---

# GitHub issue lifecycle recovery

## Inputs

Require the originating GitHub issue URL or number, the expected GitHub repository from the current checkout, an optional current branch when an OpenChamber worktree exists and no matching pull request supplies the canonical branch, retained passed validation and commit evidence naming the exact head when that branch exists remotely without a pull request, and an authenticated GitHub CLI.

The orchestrator first resolves the caller source into `/tmp/opencode/lifecycle-policy.snapshot.json`; every invocation passes that snapshot as `--policy /tmp/opencode/lifecycle-policy.snapshot.json --expected-policy-digest <digest>` and never reuses the source. It may change only validated repository-local names, sources, evidence IDs, check/visual allowlists, and delegate hints; exact-head, authenticated-actor, validation, no-auto-merge, manual-method, and fail-closed disambiguation invariants remain mandatory.

## Procedure

All lifecycle scripts import `/code/skills/github_pr_lifecycle_common.py` for fail-closed checkout identity, marker, remote-ref, JSON, and version-1 result-envelope primitives; this skill retains its operation-specific predicates and mutations.

1. Run `python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py --issue <issue> [--branch <branch>] [--validated-head <head>]`. Supply the linked worktree's current branch and retained validated head whenever publication may have been interrupted; if branch is omitted and no PR exists, the script derives only an attached non-`main` current branch and still fails closed without exact retained-head evidence.
2. Require one versioned JSON result. Require every configured Git remote `origin` fetch and effective push URL and the issue URL to belong to the checkout repository. Require every issue-referenced pull request to target `main`; never discard a wrong-base match. Require every matching pull request to be non-cross-repository with its head repository equal to the checkout repository and exactly one matching `OpenCode-Origin:` line and `Refs #` line. GitHub state is authoritative over local state whenever a matching pull request exists. The matching pull request's `headRefName` is the canonical branch; reject a conflicting caller-supplied branch. Without a matching pull request, require the caller-supplied branch to be the current clean local branch and require its local and remote head to equal retained validated-head evidence before resuming publication.
3. Resume only the returned exact next stage. `remote-branch-no-pr` first resumes issue-worktree validation in `resume-publication` mode; `open-pull-request` resumes worktree validation before ownership baseline and hosted checks; `recovered-merged-needs-reattest` requires a fresh user re-attestation of the exact immutable PR URL, branch, head, base, and claimed manual policy-selected before merge-state verification, leased cleanup when the remote branch remains, and an exact completion comment when absent; `merged-needs-close` resumes issue closure; `closed` is terminal only after verifying the unique merged pull request, absent remote branch, current lifecycle evidence, and exact completion evidence. Never infer approval, merge method, or actor from merged state.
4. Accept current and completion lifecycle comments only when every lifecycle-controlled prefix occurs exactly once with its required value and the comment was posted by the currently authenticated GitHub actor. With configured visual scenarios, current evidence must contain exact `Visual evidence: passed` and one uploaded `https://github.com/user-attachments/` Markdown before/after pair for every exact scenario key; every alt text is exactly `Before: <scenario>` or `After: <scenario>`. Accept exact `Visual evidence: not required` only when the policy configures no scenarios (browser impact is nonapplicable). GitHub CLI rewrites body-referenced local attachment paths while preserving alt text as documented at https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli; use that rewritten body as recovery evidence. Accept byte-identical repeated valid evidence, but return `blocked-unsafe` when repeated valid current or completion comments differ. Return `waiting-external` for authentication, network, or GitHub availability. Return `waiting-user-cleanup` for a dirty no-PR recovery worktree. Return `blocked-unsafe` for malformed comment shapes, multiple matches, conflicting markers or identifiers, wrong-base matches, malformed states, externally attributable merges, or retained-evidence ambiguity.

## Boundaries

- Never mutate GitHub, Git, branches, or worktrees.
- Never infer a pull request from a title alone.

## Completion

Report repository, origin fetch and push identity, authenticated actor, issue, canonical branch, matching PR and head repository, head, verified merge commit, remote-branch state, cleanup disposition when verified, lifecycle disposition, exact next stage, evidence, and blocker.
