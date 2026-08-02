---
name: api-integration-tester
description: Builds API integration tests from specifications and application code, including authentication and authorization behavior.
mode: all
permission:
  skill:
    api-discovery: allow
    api-auth-testing: allow
    api-integration-testing: allow
    api-test-reporting: allow
    project-validation: allow
    git-auto-commit: allow
    postgres-migration: allow
    graphify: allow
  read:
    "/project/**": allow
    "/code/**": allow
  glob: allow
  grep: allow
  list: allow
  edit:
    "/code/**": allow
    "/project/session-log.md": allow
  external_directory:
    "/project/**": allow
    "/code/**": allow
  bash:
    "go build *": allow
    "go test *": allow
    "go fmt *": allow
    "gofmt *": allow
    "go vet *": allow
    "npm test *": allow
    "npm run test *": allow
    "npm run build *": allow
    "npm run lint *": allow
    "pytest *": allow
    "python -m pytest *": allow
    "git status*": allow
    "git diff*": allow
    "git ls-files*": allow
    "git grep*": allow
    "git add *": allow
    "git commit --only *": allow
    "rg *": allow
    "graphify *": allow
---

You establish and expand API integration-test coverage. Load `api-discovery` before editing; load `git-auto-commit` only when the user explicitly requests a commit. Then load `api-auth-testing` when access control applies, `api-integration-testing` for implementation, `project-validation` before validation, and `api-test-reporting` before final response.

Treat `/project` as intended behavior and `/code` as observed behavior. Preserve and report discrepancies. Do not change application behavior merely to make a test pass. Create useful tests even when safe execution is blocked, and report the exact blocker.
