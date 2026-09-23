---
name: security-verification
description: Implements focused security verification for changed access control, sensitive-data, request-protection, and secret-handling behavior.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    non-production-database-fixture: allow
    project-validation: allow
inputs:
  - approved security requirements
  - caller-provided permitted security authority source and test paths
  - project security test or scan infrastructure
  - caller-provided permitted database fixture contract path when deterministic application state is required
compatibility: opencode
metadata:
  domain: security-testing
  phase: implementation
---

# Security verification

## Inputs

Require approved security requirements, caller-provided permitted security authority, source, and test paths, project security test or scan infrastructure, and a caller-provided permitted database fixture contract path when deterministic application state is required. Do not claim certification or scan coverage not actually performed.

## Deterministic workflow

```yaml
request: "Focused security verification evidence and validation result"
workflow:
  - id: "database-fixture"
    when: "After security tests are implemented when execution requires deterministic application database state."
    skill: "non-production-database-fixture"
  - id: "validate-project"
    when: "After security verification and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inspect approved security requirements, changed paths, threat-relevant boundaries, existing security tests/scanners, and safe test identities. Do not infer a control from naming or claim compliance without evidence.
2. Build an applicability matrix from changed behavior: authentication, authorization, ownership, tenancy, nested-resource relationships, secret loading, credential provenance, sensitive output, input validation, request protection, webhook verification, audit events, retention, observability, and production exclusion of test-only capabilities.
3. For each applicable access-control row, test authorized success plus unauthenticated, unauthorized, unknown identifier, wrong owner or tenant, mismatched parent and child, and wrong subtype or channel. Derive tenant scope from the authenticated principal or approved membership source, scope the first data access by tenant, and verify every nested relationship before projection.
4. Prove denial outcomes are equivalently non-disclosing: no protected fields, counts, ownership hints, distinguishable error details, unauthorized store over-read, external calls, audit entries, session changes, or domain mutations. Use test-owned identities and observable test doubles or stores.
5. For sensitive-data paths, require explicit output-field allowlists and assert redaction before errors or provider data enter responses, logs, metrics, audits, or diagnostics. Verify stable safe error classes, bounded excerpts, and correct distinctions among absent, unavailable, zero, empty, accepted, delivered, and failed.
6. For external adapters, verify approved credential provenance and rejection of prohibited ambient environment, profile, role, metadata, or transport fallback. For queued or retried work, prove later configuration changes do not alter the immutable event-time snapshot.
7. For request protections, assert only approved origin, CSRF, input, and webhook rules. Do not weaken production configuration or bypass middleware to make a test pass.
8. When startup, probe, or packaging behavior changes, verify public probes disclose only approved minimal state and test or development capabilities are absent from production composition, routes, artifacts, and startup commands.
9. Request existing static or dependency scans through `project-validation` only when supported locally and without sending source or secrets to an unapproved service. Record scanner version/configuration when available.
10. Classify each finding as implementation defect, configuration defect, test defect, approved exception, tool limitation, infrastructure blocker, or pre-existing failure. An exception requires authoritative evidence; otherwise preserve the finding.

## Required report

Report the applicability matrix, test identities/resources without secrets, commands, findings, evidence paths, exceptions, coverage limits, and blockers.
