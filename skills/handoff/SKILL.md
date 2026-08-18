---
name: handoff
description: Writes a concise handoff file for a future session; use when wrapping up or handing off work.
---

# Handoff

Use when the user asks for a handoff or the session is ending with incomplete or continuing work.

First determine the project's existing handoff convention and path. If none exists, write `/project/handoff.md` at the project root.

Overwrite or update the current handoff; do not append.

Include only:
- Goal/current state.
- Completed changes with paths.
- Changed files requiring ownership pickup, especially uncommitted files the next agent may need to review, stage, or commit with `git-auto-commit`.
- Next concrete steps.
- Decisions/constraints.
- Blockers/open questions.
- Exact validation status.

When Git is available, inspect status before writing the handoff and separate already-committed work from uncommitted changed files. For each uncommitted file, note the intended ownership/action: review, continue editing, stage, commit, leave untouched, or verify with the user. Cite paths and commands briefly. Exclude narrative, copied logs, and irrelevant history.

If no meaningful continuation is needed, say so instead of creating a file.
