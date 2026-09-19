---
name: project-validation
description: Discovers and runs the narrowest project-native formatting, build, lint, and test validation for a focused change.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: api-integration-tester
      source: /code/agents/api-integration-tester.md
      allowed_skill: project-validation
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: project-validation
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: project-validation
    - agent: merge-evidence-resolver
      source: /code/agents/merge-evidence-resolver.md
      allowed_skill: project-validation
inputs:
  - focused changed paths
  - project-native validation context
---

# Project validation

If `/code/validation.md` exists, follow it. Otherwise inspect project scripts, manifests, CI, and contributor guidance for supported validation.

1. Inspect existing scripts, manifests, CI, and contributor guidance for supported commands.
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

Do not introduce a test framework, modify production configuration, or run destructive commands merely to validate a change.
