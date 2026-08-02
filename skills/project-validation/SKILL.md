---
name: project-validation
description: Discovers and runs the narrowest project-native formatting, build, lint, and test validation for a focused change.
---

# Project validation

If `/code/validation.md` exists, follow it. Otherwise inspect project scripts, manifests, CI, and contributor guidance for supported validation.

1. Inspect existing scripts, manifests, CI, and contributor guidance for supported commands.
2. Run the narrowest formatter and focused tests covering the change.
3. Run build, lint, or broader regression checks only when relevant and safe.
4. Classify failures as change defect, pre-existing failure, environment blocker, or unknown; do not hide failures.
5. Report commands actually run, results, skipped checks, and blockers.

Do not introduce a test framework, modify production configuration, or run destructive commands merely to validate a change.
