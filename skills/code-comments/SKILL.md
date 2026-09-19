---
name: code-comments
description: Adds concise native-language documentation for public contracts and non-obvious invariants.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: code-comments
inputs:
  - bounded code paths
  - documented contract or invariant
---

# Code comments

## Completion workflow

```yaml
request: "Validated focused code documentation change"
workflow:
  - id: "validate-project"
    when: "After documentation edits and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

Document exported or public contracts and non-obvious invariants using the language's native convention. Explain purpose, constraints, side effects, and failure behavior only when code and types do not make them clear. Cite a requirement or specification only when known. Do not add boilerplate parameter, return, or test inventories; do not alter behavior.
