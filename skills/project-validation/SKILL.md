---
name: project-validation
description: Discovers and runs the narrowest project-native formatting, build, lint, and test validation for a focused change.
classification: technical
opencode_permission:
  read:
    "/code/validation.md": allow
    "/code/AGENTS.md": allow
    "/code/README.md": allow
    "/code/go.mod": allow
    "/code/package.json": allow
    "/code/Makefile": allow
    "/code/.github/**": allow
    "/code/compose*.yml": allow
    "/code/docker-compose*.yml": allow
  bash:
    "go build *": allow
    "go test *": allow
    "go fmt *": allow
    "gofmt *": allow
    "go vet *": allow
    "go list *": allow
    "go env *": allow
    "go version *": allow
    "npm test *": allow
    "npm run test *": allow
    "npm run build *": allow
    "npm run lint *": allow
    "tsc *": allow
    "tailwindcss *": allow
    "pytest *": allow
    "python -m pytest *": allow
    "make test*": allow
    "make build*": allow
inputs:
  - focused changed paths
  - project-native validation context
  - permitted validation command set
---

# Project validation

## Inputs

Require focused changed paths, project-native validation context, and a permitted validation command set. Run only commands permitted by both this contract and the caller; report unsupported checks as `skipped`.

If `/code/validation.md` exists, follow it. Otherwise inspect only the permitted root guidance and manifests named by this contract; use the caller-provided validation context for any other project-native command.

1. Inspect available permitted guidance and manifests for supported commands.
2. Run the narrowest formatter and focused tests covering the change.
3. Run build, lint, or broader regression checks only when relevant and safe.
4. Classify failures as change defect, pre-existing failure, environment blocker, or unknown; do not hide failures.
5. Report commands actually run, results, skipped checks, and blockers.

## PostgreSQL test targets

When validation requires PostgreSQL:

1. Inspect existing test configuration, scripts, CI, and Compose wiring for its target-selection and isolation rules.
2. Run the project-native test command without overriding inherited `DATABASE_URL`. Use it only when repository evidence establishes a non-production, isolated test target.
3. When no URL is configured, let only existing project test or Compose configuration consume inherited `POSTGRES_PASSWORD`. Never print it or invent connection fields such as host, port, user, or database name.
4. Only after those options are exhausted may an existing project test provisioner be used. If no safe target or provisioner exists, do not create a special database setup; skip unsafe execution and report the blocker.

When a test requires deterministic application database state, accept only the project's approved shared fixture lifecycle. Do not create or infer allocation, migration, seeding, clock, identity, reset, cleanup, or external-effect controls. If that lifecycle is absent or its target ownership is not attested, report the check as `blocked`. A migration-only target remains valid only for migration checks that do not require composed feature state.

Do not introduce a test framework, modify production configuration, or run destructive commands merely to validate a change.
