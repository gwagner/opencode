---
name: safe-code-change
description: Implements a focused code change safely in a collaborative repository. Use for bug fixes, stub completion, or small specification-driven implementation tasks.
---

# Safe code change

1. Inspect the complete affected behavior, callers, and relevant tests before editing.
2. Use requirements or specifications when they define the intended behavior.
3. Identify whether the change crosses a public, dependency, persistence, framework, or external-service boundary. Load `interface-boundaries` when it does.
4. Make the smallest complete change. Do not alter unrelated files, generated content, tests, migrations, or public APIs without task justification.
5. Preserve existing worktree changes. Never reset, restore, or delete work not created for the task.
6. Run the narrowest applicable formatter and tests. Classify failures before changing code.
7. Report changed files, validation actually run, and remaining blockers.
