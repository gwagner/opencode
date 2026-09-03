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
- All go dependencies must be vendored
 - If in a git repo, the vendor directory must be in .gitignore
