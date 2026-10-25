---
name: github-issue-close
description: Closes one existing GitHub issue and verifies its closed state.
classification: non-technical
opencode_permission:
  shell:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh issue view * --json number,title,state,url,comments": allow
    "gh issue close *": allow
    "python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py *": allow
  external_directory:
    "/code/skills/github_issue_comment_common.py": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py": allow
inputs:
  - one existing GitHub issue URL or number
  - current Git checkout for the issue repository
  - authenticated GitHub CLI
  - exact pull-request URL, head branch, head commit, and merge commit
  - exact authenticated lifecycle actor represented by the persisted completion comment
  - persisted current and completion comments proving passed required checks and delegate project-validation
  - persisted remote-cleanup outcome and verified remote-branch absence
---

# GitHub issue close

## Inputs

Require one existing GitHub issue URL or number, the current Git checkout for its repository, the exact completed pull-request URL, head branch, head commit, merge commit, and authenticated GitHub CLI. Persisted GitHub state must include current and completion comments by the exact authenticated lifecycle actor proving passed required checks, passed delegate project-validation, and the remote-cleanup outcome; the remote branch must be absent. The shared recovery command derives and revalidates that persisted actor and evidence rather than accepting caller assertions for them.

## Procedure

1. Run `gh auth status` and `gh repo view --json nameWithOwner,url`. Stop unless authentication is available and the checkout resolves exactly one repository.
2. Run `python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py --issue <issue> --completion-pr <url> --completion-head <head> --completion-branch <branch> --completion-merge-commit <merge>`. This is the shared fail-closed completion predicate: require `merged-needs-close` or already-terminal `closed`. It revalidates the issue and repository, authenticated comment actor, exact PR URL, base, branch, head, merged state and merge commit, exact completion comment, `Delegate project-validation: passed`, `Required checks: passed`, and `Remote cleanup: deleted` or `Remote cleanup: already-absent`, plus remote-branch absence.
3. Read the issue with `gh issue view <issue> --json number,title,state,url,comments`. Stop unless it belongs to the resolved repository and its comment snapshot still contains the exact completion evidence returned by recovery.
4. If recovery returned `merged-needs-close` and the issue is open, run `gh issue close <issue>`. If recovery returned `closed`, leave it unchanged.
5. Re-read the issue including comments and rerun the same recovery command. Completion requires unchanged evidence and disposition `closed`.

## Boundaries

- Never edit, comment on, label, reopen, or delete the issue.
- Never mutate an issue outside the repository resolved from the current checkout.

## Completion

Report the repository, issue URL, previous state, verified closed state, and whether a mutation occurred.
