---
name: safe-code-change
description: Implements a focused code change safely in a collaborative repository. Use for bug fixes, stub completion, or small specification-driven implementation tasks.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    project-validation: allow
inputs:
  - approved bounded change
  - affected authority
  - caller-provided permitted authority source and test paths
---

# Safe code change

## Inputs

Require an approved bounded change, affected authority, and caller-provided permitted authority, source, and test paths.

Do not use this generic procedure for an intentionally incomplete scaffold or a state-changing backend command, job, or worker workflow. The caller must select the dedicated procedure for those scopes.

## Dead-code rule

Within the approved affected source and test scope, remove unused functions and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in source. Preserve potentially live behavior and report uncertainty rather than guessing.

## Completion workflow

```yaml
request: "Safely implemented focused code change"
workflow:
  - id: "validate-project"
    when: "After implementation and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

1. Inspect the complete affected behavior, callers, and relevant tests before editing.
2. Use requirements or specifications when they define the intended behavior. State the affected user outcome before selecting the solution.
3. Identify whether the change crosses a public, dependency, persistence, framework, or external-service boundary. Apply any boundary design procedure selected by the caller before changing that boundary.
4. Make the smallest complete change that preserves or improves the documented user outcome. Do not alter unrelated files, generated content, tests, migrations, or public APIs without task justification.
5. Preserve existing worktree changes. Never reset, restore, or delete work not created for the task.
6. Use `project-validation` to run the narrowest applicable formatter and tests. Classify failures before changing code.
7. Report changed files, the affected user workflow and observable result, validation actually run, manual verification if needed, and remaining blockers.
8. Test third-party integrations with an existing test double or deterministic local mock service. Provider-sandbox checks are separate and supplement mock coverage for responses, callbacks, failures, retries, latency, and mutable state.
