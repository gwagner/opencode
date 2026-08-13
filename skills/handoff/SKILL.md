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
- Next concrete steps.
- Decisions/constraints.
- Blockers/open questions.
- Exact validation status.

Cite paths and commands briefly. Exclude narrative, copied logs, and irrelevant history.

If no meaningful continuation is needed, say so instead of creating a file.
