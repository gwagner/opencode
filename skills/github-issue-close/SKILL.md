---
name: github-issue-close
description: Closes one non-lifecycle GitHub issue and verifies its closed state.
classification: non-technical
opencode_permission:
  shell:
    "python3 /code/skills/github-issue-close/scripts/close-generic-issue.py *": allow
  external_directory:
    "/code/skills/github_pr_lifecycle_common.py": allow
    "/code/skills/github-issue-close/scripts/close-generic-issue.py": allow
inputs:
  - exact existing non-lifecycle issue identity
  - current-turn `--authorize-close`
---
# Generic GitHub issue closure
## Inputs
Require one issue that is not lifecycle-owned and an identity-bound current-turn closure authorization.
## Procedure
Run `close-generic-issue.py --issue <issue> --authorize-close`; it rereads the exact issue after mutation. Lifecycle-owned closure belongs only to `github-lifecycle-issue-close`.
## Completion
Report `closed`, `already-closed`, `waiting-external`, or `blocked-unsafe`.
