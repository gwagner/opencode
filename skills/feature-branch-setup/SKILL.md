---
name: feature-branch-setup
description: Creates one clean local feature branch from local main before a bounded SDLC change.
---

# Feature branch setup

Use once, before specification or implementation work that will change `/code/`. This skill owns only safe local branch creation; it does not implement, validate, commit task changes, merge, delete branches, or contact remotes.

1. Confirm `/code/` is a Git worktree, `HEAD` is attached to local `main`, local `main` exists, and both the worktree and index are clean. If any condition fails, report the exact blocker and stop. Never checkpoint, stash, reset, restore, clean, or reuse pre-existing work.
2. Derive one Git-valid `feature/<task-slug>` name from the requested user outcome. The slug must be concise and deterministic.
3. Confirm the branch does not already exist. If it exists, report the name and stop; never reuse, delete, or rename it.
4. Create and switch to that branch directly from local `main`. Never fetch, pull, push, use a remote, or alter local `main`.
5. Report the new feature branch and its local-main base revision.
