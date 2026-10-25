---
name: github-lifecycle-issue-close
description: Closes one lifecycle issue only after exact merged pull-request recovery evidence.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-lifecycle-issue-close/scripts/close-lifecycle-issue.py *": allow
    "python3 /code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/code/skills/github_issue_comment_common.py": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py": allow
    "/code/skills/github-lifecycle-issue-close/scripts/close-lifecycle-issue.py": allow
inputs:
  - repository/run-bound policy snapshot and digest
  - exact issue, merged PR URL, branch, head, merge commit, and lifecycle actor identity
  - current-turn identity-bound `--authorize-closure`
---
# Lifecycle issue closure
## Inputs
Require the listed exact identities after the closure ask.
## Procedure
Re-run authoritative lifecycle recovery before and after the only close mutation; reject nonmatching actor, comments, cleanup, policy, or merge identity.
## Completion
Report `closed`, `already-closed`, `waiting-external`, or `blocked-unsafe` with recovery envelopes.
