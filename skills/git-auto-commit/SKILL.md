---
name: git-auto-commit
description: Creates a safe, verbose Git commit for agent-owned validated changes when the user explicitly requests a commit.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: api-integration-tester
      source: /code/agents/api-integration-tester.md
      allowed_skill: git-auto-commit
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: git-auto-commit
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: git-auto-commit
inputs:
  - explicit commit authorization
  - ownership baseline
  - passed validation
---

# Git auto-commit

Use only when the user explicitly requests a commit, after a recorded ownership baseline and passed project validation. This skill owns final staging and commit only.

In todo-loop work, ownership is iteration-scoped: record a baseline before editing in every iteration and commit that iteration before returning CONTINUE or DONE. The loop may create a safety checkpoint for work left after a clean iteration baseline; that checkpoint does not transfer unrelated pre-existing work to the agent.

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
