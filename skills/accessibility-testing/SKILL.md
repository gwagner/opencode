---
name: accessibility-testing
description: Implements focused accessibility checks for changed rendered frontend behavior.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    project-validation: allow
inputs:
  - affected rendered routes or components
  - approved interaction and content requirements
  - project accessibility test infrastructure
  - caller-provided permitted accessibility authority source and test paths
compatibility: opencode
metadata:
  domain: frontend-accessibility
  phase: implementation
---

# Accessibility testing

## Inputs

Require affected rendered routes or components, approved interaction and content requirements, project accessibility test infrastructure, and caller-provided permitted accessibility authority, source, and test paths. Report blocked when no safe runnable target exists.

## Deterministic workflow

```yaml
request: "Focused accessibility test evidence and validation result"
workflow:
  - id: "validate-project"
    when: "After accessibility checks and every selected post-change check."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

## Procedure

1. Inspect the changed rendered surface, approved interaction/content criteria, existing accessibility tests, scanner configuration, and runnable test target. Do not introduce a scanner or browser harness without approval.
2. Build an applicability matrix: native semantic structure, accessible name, role/state/value, one accessible action path, keyboard operation, focus order and preservation, visible focus, error identification, loading and recovery status announcement, color-independent meaning, and target-size or contrast checks only when supported by repository tooling.
3. For each applicable row, identify the user action and expected assistive-technology-visible outcome from the approved criteria. Mark unsupported checks `skipped`, not passed.
4. Use `project-validation` to run the established automated scan against deterministic fixture states. Treat each finding as a defect unless an approved, documented exception identifies the affected element, rationale, owner, and review date.
5. Exercise changed keyboard flows through the project test harness: reachable control, expected activation, focus destination after navigation/dialog/error changes, and escape or recovery behavior when specified. Do not claim screen-reader behavior that was not actually tested.
6. Verify changed form controls have an accessible name, required/error state is exposed, and error text identifies the correction when those behaviors are in scope. For refreshed regions, verify status and focus behavior without discarding applicable input, selection, modal identity, or context.
7. Classify failures as accessibility defect, test defect, approved exception, tool limitation, infrastructure blocker, or pre-existing failure. Never hide a violation by weakening assertions or disabling rules.

## Required report

Report the applicability matrix, scanner and keyboard commands, findings with affected paths, approved exceptions, unsupported/skipped checks, and blockers.
