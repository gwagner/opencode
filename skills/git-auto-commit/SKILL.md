---
name: git-auto-commit
description: Creates a safe, verbose Git commit for agent-owned validated changes when the user explicitly requests a commit.
classification: technical
opencode_permission:
  read: allow
  bash:
    "git status*": allow
    "git diff*": allow
    "git add -- *": allow
    "git commit --only *": allow
inputs:
  - explicit commit authorization
  - ownership baseline
  - passed validation
---

# Git auto-commit

## Inputs

Require explicit commit authorization, an ownership baseline, and passed validation.

Use only when the user explicitly requests a commit, after a recorded ownership baseline and passed project validation. This skill owns final staging and commit only.

1. Confirm the recorded baseline has an empty index. Preserve all pre-existing worktree paths and exclude them from this commit.
2. Track only files created or edited by this agent after the baseline. Do not commit when ownership of a changed path is uncertain.
3. Confirm `project-validation` and every task-required check passed. Do not commit after a failed, blocked, or required-but-skipped check.
4. Recheck status and diff. Stage only tracked, baseline-clean paths with `git add -- <paths>`.
5. Commit only those paths with `git commit --only ... -- <paths>`. Never use reset, restore, clean, stash, amend, or push.
6. Use a descriptive subject and body containing:
   - Summary of behavior changed.
   - Files changed, with each file's purpose.
   - Why the change was made.
   - Validation commands and passing results.

If no eligible changes remain, Git identity is unavailable, or any safety gate fails, do not commit; report the exact reason.
