---
name: tailwind
description: Configures Tailwind standalone CLI input, content scanning, generated CSS output, and backend static-file serving.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: tailwind
inputs:
  - approved frontend build scope
  - source and output paths
---

# Tailwind standalone CLI

## Completion workflow

```yaml
request: "Validated Tailwind standalone configuration"
workflow:
  - id: "validate-project"
    when: "After configuration, generation, and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

Use when a TypeScript or server-rendered frontend needs generated Tailwind CSS without a bundler.

1. Locate the project-approved standalone CLI and declare its CSS input and generated output paths.
2. Scan every source that emits classes, including TypeScript, HTML, and server templates.
3. Keep generated CSS outside handwritten source paths and exclude it from content scanning.
4. Add focused build/watch commands only when supported by repository tooling.
5. Confirm the backend serves the generated output as a static asset with a stable URL.
