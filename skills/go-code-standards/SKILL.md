---
name: go-code-standards
description: Use when adding or modifying Go to apply focused idiomatic Go code standards.
---

# Go Code Standards

- Write idiomatic Go and format with `gofmt`.
- Handle errors explicitly and add useful context when returning them.
- Propagate `context.Context` through operations that may block or call dependencies.
- For dependency interfaces and test seams, follow `interface-boundaries`; keep Go interfaces small and consumer-owned.
- Use table-driven tests where suitable.
- Avoid `panic` for ordinary errors and needless abstractions.
- Follow the repository's declared Go module and dependency policy; this skill does not establish vendoring or Git-tracking policy.
