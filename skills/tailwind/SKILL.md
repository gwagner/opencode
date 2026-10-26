---
name: tailwind
description: Configures Tailwind standalone CLI input, content scanning, generated CSS output, and backend static-file serving.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  edit: allow
  bash:
    "tailwindcss *": allow
    go build *: allow
    go test *: allow
    go fmt *: allow
    gofmt *: allow
    go vet *: allow
    go list *: allow
    go env *: allow
    go version *: allow
    npm test *: allow
    npm run test *: allow
    npm run build *: allow
    npm run lint *: allow
    tsc *: allow
    pytest *: allow
    python -m pytest *: allow
    make test*: allow
    make build*: allow
inputs:
  - approved frontend build scope
  - caller-provided permitted source and output paths
---

# Tailwind standalone CLI

## Inputs

Require approved frontend build scope and caller-provided permitted source and output paths.

## Dead-code rule

Within the approved affected handwritten source and test scope, remove unused modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in source. Preserve generated output and potentially live behavior; report uncertainty rather than guessing.

## Completion workflow

```yaml
request: "Validated Tailwind standalone configuration"
workflow:
```

Use when a TypeScript or server-rendered frontend needs generated Tailwind CSS without a bundler.

1. Locate the project-approved standalone CLI and declare its CSS input and generated output paths.
2. Scan every source that emits classes, including TypeScript, HTML, and server templates.
3. Keep generated CSS outside handwritten source paths and exclude it from content scanning. Never patch generated CSS directly; change handwritten source or configuration and regenerate it.
4. Add focused build/watch commands only when supported by repository tooling.
5. Confirm one declared embed or packaging owner supplies the same generated output to production, tests, and browser validation, and that the application serves it as a current same-origin static asset from a stable, working-directory-independent URL.
