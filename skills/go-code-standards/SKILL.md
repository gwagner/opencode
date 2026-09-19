---
name: go-code-standards
description: Use when adding or modifying Go to apply focused idiomatic Go code standards.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: go-code-standards
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: go-code-standards
inputs:
  - bounded Go change
  - repository Go conventions
---

# Go Code Standards

## Deterministic workflow

```yaml
request: "Idiomatic Go change with focused dependency seams"
workflow:
  - id: "define-dependency-boundaries"
    when: "When adding dependency interfaces or test seams."
    skill: "interface-boundaries"
  - id: "validate-project"
    when: "After all selected post-change stages."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

- Write idiomatic Go and format with `gofmt`.
- Handle errors explicitly and add useful context when returning them.
- Propagate `context.Context` through operations that may block or call dependencies.
- For dependency interfaces and test seams, follow `interface-boundaries`; keep Go interfaces small and consumer-owned.
- Use table-driven tests where suitable.
- Avoid `panic` for ordinary errors and needless abstractions.
- Follow the repository's declared Go module and dependency policy; this skill does not establish vendoring or Git-tracking policy.
