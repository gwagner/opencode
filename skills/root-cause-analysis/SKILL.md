---
name: root-cause-analysis
description: Establishes the evidenced causal mechanism of one reported software defect before a corrective change is selected.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
inputs:
  - one reported defect and observed symptom
  - incident time window environment and build or release version when available
  - expected behavior or authoritative behavior source when available
  - caller-permitted investigation paths
  - available log metric trace reproduction runtime or test evidence
---

# Root-cause analysis

## Inputs

Require one reported defect and observed symptom; incident time window, environment, and build or release version when available; expected behavior or authoritative behavior source when available; caller-permitted investigation paths; and available log, metric, trace, reproduction, runtime, or test evidence.

Use `read`, `glob`, and `grep` only within caller-permitted investigation paths. Do not edit evidence, source, configuration, or runtime state.

## Procedure

1. Establish the incident envelope: symptom, affected workflow, first and last observed time, environment, build or release version, frequency, affected scope, expected behavior, and each evidence source. Mark unavailable values and unknown expected behavior explicitly; do not fabricate them.
2. Separate confirmed observations from assumptions. Classify each artifact as log, metric, trace, reproduction, test, code, configuration, or authority evidence. Do not treat a stack trace, failing assertion, alert, or visible symptom as the cause.
3. When logs are available, perform bounded triage in this order:
   1. Restrict evidence to the incident envelope before widening the time, environment, version, component, event-code, or correlation scope.
   2. Group events by stable event code, owning component, operation, outcome, error class, environment, and version. Record count plus first and last occurrence; do not use variable message text as identity.
   3. Reconstruct each relevant request, job, or workflow by correlation, trace, span, parent, or cause identifiers. Order events by causal links when available; do not infer cross-system order from timestamps alone when clock synchronization is unproven.
   4. Mark the earliest observed failure, each propagated or duplicate report, retries, degraded fallbacks, and recovery. Treat missing expected events as missing evidence, not proof that the event did not occur.
   5. Compare at least one failing execution with a successful execution from the same relevant version and environment when available; otherwise record the comparison limitation.
4. Trace the earliest observed failure through permitted code, configuration, tests, interfaces, dependencies, and runtime wiring. Distinguish the originating mechanism, contributing conditions, and downstream symptoms.
5. Build a hypothesis table with one row per plausible causal mechanism: supporting evidence, contradicting evidence, falsifying check, result, and remaining limitation. Reject contradicted hypotheses; do not select by plausibility alone.
6. Identify the earliest controllable mechanism in the proven causal chain. Define affected scope, corrective direction, and regression evidence that would distinguish correction from symptom suppression.
7. If evidence is insufficient, request the smallest diagnostic addition by naming the exact event, field, level, component or correlation scope, duration, and redaction constraint. Do not request unrestricted production verbosity or modify runtime logging through this skill.
8. Stop without proposing implementation when the causal mechanism remains unproven or intended behavior is ambiguous. Report the exact missing evidence or authority and the next falsifying check.

## Output

Report the incident envelope, confirmed symptom, expected behavior status, event clusters, reconstructed timeline, earliest observed failure, originating mechanism, contributing conditions, propagated symptoms, hypothesis table, causal chain, root-cause confidence, evidence and limitations, affected scope, corrective direction, required regression evidence, and any bounded diagnostic request. This skill does not edit code, change runtime verbosity, or select an implementation procedure.
