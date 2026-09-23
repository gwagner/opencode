---
name: postgres-migration-integration-testing
description: Validates changed PostgreSQL migrations and schema-dependent behavior against an isolated project-native test target.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  skill:
    non-production-database-fixture: allow
    project-validation: allow
inputs:
  - caller-provided permitted migration source and test paths
  - migration history
  - isolated project-native PostgreSQL test target
  - caller-provided permitted database fixture contract path when composed feature state is required
compatibility: opencode
metadata:
  domain: database-testing
  database: postgresql
  phase: implementation
---

# PostgreSQL migration integration testing

## Inputs

Require caller-provided permitted migration, source, and test paths, migration history, an isolated project-native PostgreSQL test target, and a caller-provided permitted database fixture contract path when composed feature state is required. Never create or infer connection settings; report blocked when isolation is unproven.

Execute the migration test plan only through the final `project-validation` stage and its caller-permitted project-native command set.

## Deterministic workflow

```yaml
request: "Isolated PostgreSQL migration test evidence and validation result"
workflow:
  - id: "database-fixture"
    when: "After migration checks are prepared when execution requires deterministic composed feature state rather than a migration-only target."
    skill: "non-production-database-fixture"
  - id: "validate-project"
    when: "After migration integration checks and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inspect migration history, changed migrations, migration runner, CI/test configuration, and target-selection logic. Establish the exact isolated target from repository evidence. If the target could be shared or production, stop with `blocked`.
2. Record the migration test plan: baseline revision, changed migration paths, expected schema objects, expected data transformation or preservation behavior, affected application query, and correction path for a failed deployment.
3. Provision or reset only through the approved shared test lifecycle or a separately approved migration-only lifecycle that proves fresh isolated ownership. Do not construct a connection string, override inherited database configuration, truncate arbitrary data, or run a migration command outside the verified isolated target.
4. Apply the baseline history using the repository runner, seed only test-owned fixture data when preservation behavior is relevant, then apply the changed migration sequence exactly once.
5. Assert migration ordering and successful completion. Verify each changed table, column, type, constraint, index, policy, function, or trigger through repository-supported schema inspection or affected application behavior.
6. Verify required data preservation, backfill, nullability transition, uniqueness, foreign-key, policy, and query behavior using the approved migration plan. For concurrency-sensitive invariants, test the database guard under a race. For ordered reads, test the complete persisted tie-breaker across equal-value page boundaries. Do not claim rollback success unless the repository supports and executes a rollback/correction test.
7. Confirm no existing migration file changed and identify lock, compatibility, or staged-deployment risks from the migration contract.
8. Classify failures as migration defect, application defect, fixture/test defect, unsafe target, infrastructure blocker, or pre-existing failure.

## Required report

Report target-isolation evidence, baseline and upgraded revisions, migration commands, schema/data assertions, affected-query result, unchanged-history check, risks, and blockers.
