---
name: code-comments
description: Adds concise native-language documentation for public contracts and non-obvious invariants.
classification: non-technical
opencode_permission:
  read: allow
  edit: allow
  bash:
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
    tailwindcss *: allow
    pytest *: allow
    python -m pytest *: allow
    make test*: allow
    make build*: allow
inputs:
  - caller-provided permitted read and edit paths
  - bounded code paths
  - documented contract or invariant
---

# Code comments

## Inputs

Require caller-provided permitted read and edit paths.

Require bounded code paths and the documented contract or invariant.

## Dead-code rule

Within the approved affected source scope, remove commented-out code and reference-only logic; use Git history for reference. Preserve potentially live behavior and report uncertainty rather than guessing.

## Completion workflow

```yaml
request: "Validated focused code documentation change"
workflow:
```

Document exported or public contracts and non-obvious invariants using the language's native convention. Explain purpose, constraints, side effects, and failure behavior only when code and types do not make them clear. Cite a requirement or specification only when known. Do not add boilerplate parameter, return, or test inventories; do not alter behavior.
