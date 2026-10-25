---
name: github-issue-comment
description: Posts one verified non-lifecycle comment to an existing GitHub issue.
classification: non-technical
opencode_permission:
  shell:
    "python3 /code/skills/github-issue-comment/scripts/post-generic-comment.py *": allow
    "rm -f /tmp/opencode/github-issue-manager-comment.md": allow
  read:
    "/tmp/opencode/github-issue-manager-comment.md": allow
  edit:
    "/tmp/opencode/github-issue-manager-comment.md": allow
  external_directory:
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-issue-comment/scripts/post-generic-comment.py": allow
inputs:
  - exact existing issue identity
  - caller-provided generic body with stable idempotency identity
  - current-turn `--authorize-comment`
---
# Generic GitHub issue comment
## Inputs
Require one non-lifecycle body containing exactly `OpenCode-Comment-ID: <identity>` and a current-turn authorization.
## Procedure
Write the body as data, then run `post-generic-comment.py --issue <issue> --identity <identity> --authorize-comment`. It rejects lifecycle evidence markers; those belong only to `github-lifecycle-issue-evidence`.
## Completion
Report `posted` or `reused` with the verified issue comment.
