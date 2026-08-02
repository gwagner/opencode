---
name: git-auto-commit
description: Creates a safe, verbose Git commit for agent-owned validated changes when the user explicitly requests a commit.
---

# Git auto-commit

Use only when the user explicitly requests a commit. Load before the first edit when used; this skill owns the candidate file list.

1. Record `git status --porcelain=v1 -z` and require an empty index. Preserve all pre-existing worktree changes; exclude every path present in the baseline from this commit.
2. Track only files created or edited by this agent after the baseline. Do not commit when ownership of a changed path is uncertain.
3. Run `project-validation` and all task-required checks. Commit only when each applicable check passes. Do not commit after a failed, blocked, or required-but-skipped check.
4. Recheck status and diff. Stage only tracked, baseline-clean paths with `git add -- <paths>`.
5. Commit only those paths with `git commit --only ... -- <paths>`. Never use reset, restore, clean, stash, amend, or push.
6. Use a descriptive subject and body containing:
   - Summary of behavior changed.
   - Files changed, with each file's purpose.
   - Why the change was made.
   - Validation commands and passing results.

If no eligible changes remain, Git identity is unavailable, or any safety gate fails, do not commit; report the exact reason.
