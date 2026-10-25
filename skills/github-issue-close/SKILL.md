---
name: github-issue-close
description: Closes one existing GitHub issue and verifies its closed state.
classification: technical
opencode_permission:
  shell:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh issue view * --json number,title,state,url,comments": allow
    "python3 /code/skills/github-issue-close/scripts/close-issue.py *": allow
    "python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
    "/code/skills/github_issue_comment_common.py": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py": allow
    "/code/skills/github-issue-close/scripts/close-issue.py": allow
inputs:
  - one existing GitHub issue URL or number
  - current Git checkout for the issue repository
  - authenticated GitHub CLI
  - exact pull-request URL, head, branch, and merge commit from the current lifecycle run
  - current-turn explicit closure authorization
---

# GitHub issue close

## Inputs

Require one existing GitHub issue URL or number, the current Git checkout for its repository, the exact completed pull-request URL, head branch, head commit, merge commit, authenticated GitHub CLI, and a current-turn explicit closure authorization. Persisted GitHub state must include current and completion comments by the exact authenticated lifecycle actor proving passed required checks, passed delegate project-validation, and the remote-cleanup outcome; the remote branch must be absent. The shared recovery command derives and revalidates that persisted actor and evidence rather than accepting caller assertions for them.

## Procedure

1. Run `gh auth status` and `gh repo view --json nameWithOwner,url`. Stop unless authentication is available and the checkout resolves exactly one repository.
2. Run `python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py --issue <issue> --completion-pr <url> --completion-head <head> --completion-branch <branch> --completion-merge-commit <merge>`. This is the shared fail-closed completion predicate: require `merged-needs-close` or already-terminal `closed`. It revalidates the issue and repository, authenticated comment actor, exact PR URL, base, branch, head, merged state and merge commit, exact completion comment, `Delegate project-validation: passed`, `Required checks: passed`, and `Remote cleanup: deleted` or `Remote cleanup: already-absent`, plus remote-branch absence.
3. If recovery returned `merged-needs-close`, run `python3 /code/skills/github-issue-close/scripts/close-issue.py --issue <issue> --expected-pr <url> --expected-head <head> --expected-branch <branch> --expected-merge-commit <merge> --authorize-closure`. The script snapshots and hashes the read-only policy source, re-runs recovery immediately before mutation, closes with the recovery-bound `--repo`, then re-runs recovery after mutation. A changed policy digest blocks completion. It never reads caller-supplied recovery JSON.
4. If recovery returned `closed`, or completion is `comment-only` or `none`, leave the issue unchanged.

## Boundaries

- Never edit, comment on, label, reopen, or delete the issue.
- Never accept a policy file, prior turn, or caller-supplied JSON as mutation authorization.
- Never mutate an issue outside the repository resolved from the current recovery read.

## Completion

Report the repository, issue URL, previous state, verified closed state, and whether a mutation occurred.
