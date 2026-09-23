---
name: release-readiness-validation
description: Validates changed delivery artifacts, runtime configuration, migration ordering, health checks, and observability wiring.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  skill:
    project-validation: allow
inputs:
  - caller-provided permitted delivery runtime source and test paths
  - approved operational requirements
  - project-native build and validation tooling
compatibility: opencode
metadata:
  domain: release-validation
  phase: implementation
---

# Release readiness validation

## Inputs

Require caller-provided permitted delivery, runtime, source, and test paths, approved operational requirements, and project-native build and validation tooling. This skill validates artifacts only; it does not deploy, push, or contact a remote.

## Deterministic workflow

```yaml
request: "Release-readiness evidence and validation result"
workflow:
  - id: "validate-project"
    when: "After release-readiness checks and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inventory changed delivery artifacts and approved operational requirements: build manifest, container definition, deployment descriptor, environment schema, startup/shutdown wiring, migration execution, health/readiness endpoint, log/metric/trace configuration, and scheduled-job configuration.
2. Build an applicability matrix. Every changed artifact must map to one repository-supported local validation command or an explicit `skipped`/`blocked` reason. Do not invent environment values, deployment tooling, or remote targets.
3. Use `project-validation` to run the narrowest project-native build, manifest syntax, configuration, and container validation commands. Keep credentials absent from command output and artifacts.
4. For changed startup or runtime wiring, verify mandatory migration and initialization barriers complete before serving or worker execution; initial failure exits nonzero; readiness remains false through recovery barriers; and liveness may remain independent when authority permits it.
5. For public probes, verify fixed minimal no-store responses from in-memory snapshots and zero database, migration, listener, retry, recovery, or provider work per request.
6. Inspect production composition roots, route tables, artifacts, images, and startup commands for structural absence of test or development registries, brokers, seeders, bootstrap identities, unrestricted error-ingest routes, destructive helpers, and fixture capabilities. An approved production interaction-log endpoint is permitted only when its bounded business-event default and controlled diagnostic override satisfy the operational contract.
7. For generated or embedded frontend assets, identify handwritten source, exact regeneration command, generated output, one embed or packaging owner, serving route, and source-to-generated-to-packaged-to-served parity. Fail direct generated-output-only repair.
8. For changed observability wiring, verify stable classifications, approved fields, bounded samples, explicit truncation, low-cardinality labels, expected-control-flow distinction, redaction before emission, and non-recursive failure handling where local validation exists. Report unsupported remote-only checks as `skipped`.
9. For changed end-user interaction logging, verify the approved environment variable and allowlisted values, safe missing and invalid configuration behavior, backend-supplied frontend mode and catalog, development diagnostic coverage, production named-business-event default, bounded same-origin ingestion, authentication and request protection, untrusted-input validation and redaction, trusted server enrichment, prohibited-data exclusion, bounded queue, request, batch, retry, rate, volume, and retention behavior, structured application-logger emission, deployment-owned sink routing, and tests for each supported mode and failure boundary. A production diagnostic override passes only with explicit authorization, scope, expiry, access control, activation and deactivation audit evidence, and automatic restoration evidence.
10. Review backward compatibility: additive configuration, default behavior, migration compatibility, and rollback/correction guidance. Do not claim a deployment or rollback was executed unless it was.
11. Classify outcomes as artifact defect, configuration defect, validation defect, infrastructure blocker, pre-existing failure, skipped, or passed.

## Required report

Report the applicability matrix, changed artifacts, commands, configuration values intentionally omitted, migration/startup evidence, observability evidence, compatibility risks, outcomes, and blockers.
