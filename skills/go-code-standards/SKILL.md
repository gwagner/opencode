---
name: go-code-standards
description: Use when adding or modifying Go to apply focused idiomatic Go code standards.
classification: technical
opencode_permission:
  read: allow
  edit: allow
  bash:
    "gofmt *": allow
    "go test *": allow
  skill:
    interface-boundaries: allow
    project-validation: allow
inputs:
  - bounded Go change
  - repository Go conventions
---

# Go Code Standards

## Inputs

Require a bounded Go change and repository Go conventions.

## Dead-code rule

Within the approved affected Go source and test scope, remove unused functions and packages, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in source. Preserve potentially live behavior and report uncertainty rather than guessing.

## Source authority

Apply [Effective Go](https://go.dev/doc/effective_go) as idiom guidance. It was written for Go's 2009 release and does not cover modules or generics; the current Go specification, release notes, and repository conventions govern those topics.

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

- Format changed Go with `gofmt`; do not manually preserve a competing layout.
- Use short, lower-case single-word package names; use `MixedCaps` rather than underscores; avoid repeating a package name in its exported identifiers.
- Name getters `Field`, not `GetField`; reserve established method names such as `Read`, `Write`, `Close`, and `String` for their conventional meaning and signature.
- Keep the successful path unindented: return handled errors early and omit an `else` after a terminating branch.
- Handle errors explicitly and add useful context when returning them; use `panic` only for genuinely unrecoverable failures.
- Prefer types with useful zero values. Use `make` for initialized maps, slices, and channels; use `new` when a pointer allocation is required.
- Use slices for variable-length sequences; remember that slices and maps share referenced storage, and return a slice after an append that may reallocate it.
- Keep receiver choice consistent for a type; use a pointer receiver when mutation, non-copyability, or efficiency requires it.
- Propagate `context.Context` through operations that may block or call dependencies.
- For dependency interfaces and test seams, follow `interface-boundaries`; keep Go interfaces small and consumer-owned.
- Use table-driven tests where suitable.
- Avoid needless abstractions.
- Follow the repository's declared Go module and dependency policy; this skill does not establish vendoring or Git-tracking policy.
