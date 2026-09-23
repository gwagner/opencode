---
name: api-resilience-testing
description: Implements focused tests for approved API idempotency, retry, timeout, webhook, duplicate-delivery, and upstream-failure behavior.
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
  - approved resilience contract
  - selected API or integration scope
  - controllable safe test dependencies
  - caller-provided permitted resilience authority source and test paths
  - caller-provided permitted database fixture contract path when deterministic application state is required
compatibility: opencode
metadata:
  domain: api-testing
  phase: resilience
---

# API resilience testing

## Inputs

Require an approved resilience contract, selected API or integration scope, controllable safe test dependencies, caller-provided permitted resilience authority, source, and test paths, and a caller-provided permitted database fixture contract path when deterministic application state is required. Do not infer retry count, timeout, idempotency key behavior, or webhook signature rules.

## Dead-code rule

Within the approved affected test scope, remove unused test helpers and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in tests. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "Focused API resilience tests and validation result"
workflow:
  - id: "database-fixture"
    when: "After resilience tests are implemented when execution requires deterministic application database state."
    skill: "non-production-database-fixture"
  - id: "validate-project"
    when: "After API resilience tests and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inspect the approved resilience contract, selected route/integration scope, retry/timeout/idempotency semantics, webhook verification rules, existing test doubles, and safe local dependency controls. Stop with `blocked` when a required behavior or controllable dependency is unspecified.
2. Build a resilience matrix. For each selected behavior, record trigger, controlled dependency response, credential provenance, event-time snapshot fields, stable event or idempotency identity, permitted attempts or deadline, expected response/event, permitted side effects, duplicate behavior, and terminal error mapping.
3. Reuse existing test doubles, local servers, fake clocks, queues, and fixtures. If no controllable dependency exists, report `blocked`; never call a live third-party endpoint or change production retry configuration.
4. For idempotency, submit the specified repeated request/key pattern and assert the contract-defined response and exactly the permitted durable or external side effect count.
5. For retries/timeouts, force each contract-defined transient, permanent, and timeout condition. Assert bounded attempts, no retry for terminal errors when specified, deadline/error mapping, cleanup of in-flight state, and reuse of the original immutable destination, recipient, payload, signing/configuration revision, and event identity after later configuration changes.
6. For webhooks, use test-only payloads and signatures. Assert valid acceptance, invalid/missing signature rejection, duplicate delivery behavior, ordering behavior only when specified, and no side effect before required verification.
7. For external credentials, assert the adapter receives only explicitly authorized configuration and rejects prohibited ambient environment, profile, role, metadata, or transport fallback.
8. For upstream failures, assert stable mapping, bounded redacted diagnostics, no credential leakage, and the documented recovery or retry signal. Never assert arbitrary implementation timing.
9. Use `project-validation` to run focused tests and the relevant existing integration suite when safe. Classify failures as implementation defect, contract mismatch, test-double defect, unsafe dependency blocker, infrastructure blocker, or pre-existing failure.

## Required report

Report the resilience matrix, dependency-control evidence, test paths, commands, attempts/side-effect assertions, outcomes, skipped rows, and blockers.
