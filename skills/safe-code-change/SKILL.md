---
name: safe-code-change
description: Implements a focused code change safely in a collaborative repository. Use for bug fixes, stub completion, or small specification-driven implementation tasks.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: safe-code-change
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: safe-code-change
inputs:
  - approved bounded change
  - affected code and authority
---

# Safe code change

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
6. Run the narrowest applicable formatter and tests. Classify failures before changing code.
7. Report changed files, the affected user workflow and observable result, validation actually run, manual verification if needed, and remaining blockers.
8. Test third-party integrations with an existing test double or deterministic local mock service. Provider-sandbox checks are separate and supplement mock coverage for responses, callbacks, failures, retries, latency, and mutable state.
