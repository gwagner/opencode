---
name: frontend-behavior-testing
description: Implements focused tests for approved frontend interaction, state, validation, error, and recovery behavior.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    project-validation: allow
inputs:
  - approved frontend acceptance criteria
  - affected routes or components
  - project test infrastructure
  - caller-provided permitted frontend authority source and test paths
compatibility: opencode
metadata:
  domain: frontend-testing
  phase: implementation
---

# Frontend behavior testing

## Inputs

Require approved frontend acceptance criteria, affected routes or components, project test infrastructure, and caller-provided permitted frontend authority, source, and test paths. Stop and report a missing behavioral contract or safe test target.

## Dead-code rule

Within the approved affected test scope, remove unused test helpers and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in tests. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "Focused frontend behavior tests and validation result"
workflow:
  - id: "validate-project"
    when: "After frontend behavior tests and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inspect the changed route/component, approved criteria, existing frontend tests, test runner, fixtures, and documented local route startup. Do not add a test framework.
2. Build one behavior matrix. For each changed async region or user action, record ownership boundary, initial loading, populated, empty, pending, error, recovery, last-known-good behavior, precondition, action, observable result, and required fixture. Empty is not error. Omit a row only when approved criteria prove it is inapplicable.
3. Select the narrowest existing test level that can observe the outcome: component, browser, or existing end-to-end harness. If no established harness can safely exercise the required outcome, report `blocked`; do not substitute manual testing for automated evidence.
4. Create or reuse deterministic fixtures. Stub only the boundary owned by the test; do not stub the component behavior under test, call production services, share mutable records, or depend on execution order.
5. Build a preservation matrix for applicable draft input, selection, page, filter, range, modal identity, focus, scroll, and unaffected sibling content. Refresh only the owning boundary and retain last-known-good content after a post-load failure when required.
6. Implement one test per behavior and preservation row. Assert visible content, native semantics, stable behavior hooks, enabled/disabled state, navigation, submitted data, error presentation, status announcement, focus behavior, loading completion, and recovery only when specified. Do not assert framework implementation details, generated class names, or timing guesses.
7. When an interaction logging contract applies, test each affected trigger and outcome against the approved event code, schema version, allowlisted fields, effective environment mode, batching boundary, and drop behavior. Assert prohibited fields are absent, the browser cannot select a more permissive mode or trusted context, duplicate handlers do not double-emit, and unavailable or rejected telemetry does not change visible success, failure, focus, navigation, or recovery behavior.
8. For asynchronous behavior, wait on an observable completed state supplied by the existing harness. Never use arbitrary sleep-based success criteria.
9. Use `project-validation` to run the narrowest affected test file or command before broader checks. Classify failures as test defect, implementation defect, contract mismatch, infrastructure blocker, or pre-existing failure. Change application behavior only when the approved contract requires it.

## Required report

Report behavior-matrix coverage, test paths, fixtures, commands, result per command, skipped matrix rows with rationale, and blockers.
