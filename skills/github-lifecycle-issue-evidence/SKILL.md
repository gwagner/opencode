---
name: github-lifecycle-issue-evidence
description: Posts and verifies one exact actor-bound GitHub issue lifecycle evidence comment.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-lifecycle-issue-evidence/scripts/post-lifecycle-evidence.py *": allow
    "rm -f /tmp/opencode/github-issue-manager-comment.md": allow
  read: allow
  edit:
    "/tmp/opencode/github-issue-manager-comment.md": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/code/skills/github_issue_comment_common.py": allow
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-lifecycle-issue-evidence/scripts/post-lifecycle-evidence.py": allow
inputs:
  - repository/run-bound policy snapshot and digest
  - exact issue, pull request, head, lifecycle comment kind, and current actor identity
  - authorized exact comment body and optional visual evidence manifest
---
# Lifecycle issue evidence
## Inputs
Require the listed immutable identities and `--authorize-comment` immediately after the identity-bound ask.
## Procedure
Run the script only with `--kind current` or `--kind completion`; it rejects generic comments, validates exact lifecycle IDs, actor-owned existing evidence, and authoritative reread results.
## Completion
Report the exact verified comment ID, actor, policy binding, and disposition.
