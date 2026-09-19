---
name: evidence-based-merge-resolution
description: Resolves local-main merge conflicts in the current checkpointed feature branch using authoritative evidence, validation, and an explicit local-main tie-breaker.
---

# Evidence-based merge resolution

Use only after `git-main-sync` has created a checkpoint commit and a local-`main` merge is conflicted in the current feature worktree. Resolve and commit that merge directly on the feature branch. Never use a remote, reset, restore, clean, stash, amend, rewrite history, or resolve uncommitted work that predates the checkpoint.

1. Record feature branch, checkpoint object ID, local `main` object ID, merge-base, status, conflict paths, and Git conflict types. Confirm the conflict is the active local-`main` merge and preserve the checkpoint as the feature-side parent.
2. For every conflict, gather only relevant evidence in this order: approved requirements; approved specifications and contracts; focused tests; public interfaces and callers; migration history; implementation history and blame. Record path:line or commit citations for evidence used.
3. Generate local-main, source, and combined candidates. Use a combined candidate only when cited authority requires it and focused validation supports it. Resolve generated artifacts from their source and regeneration command, never by hand. For rename/delete, binary, submodule, symlink, and mode conflicts, use their declared owner, source of truth, pinned version, or callers as applicable.
4. When evidence is absent, contradictory, or does not select one candidate, select local `main` (`theirs` in this merge). This is the required deterministic tie-breaker. The feature-side version remains preserved by the checkpoint parent; never discard, reset, or rewrite that history.
5. Stage only resolved conflict paths. Run `git diff --check` and the narrowest relevant formatter, build, test, contract, migration, or regeneration checks. Diagnose and repair failures caused by the merge when evidence supports a bounded correction, then rerun affected checks. Commit one merge-resolution commit with checkpoint and local-main object IDs, per-path decision summaries, evidence citations, tie-breaker use, repairs, and validation results.
6. If validation still fails or cannot run, commit the mechanically and evidentially resolved merge, mark validation failed or blocked, and report exact commands, paths, and corrective work. Do not overwrite the checkpoint or change unrelated behavior. A validation failure is not proof that another conflicting version is correct.

## Completion

Return feature branch, checkpoint, local-main, and merge-resolution object IDs, conflict paths, candidate selected per path, citations, repairs, validation results, and whether the local-main tie-breaker was used. The current feature branch remains the loop branch.
