---
name: frontend-impact-validation
description: Evaluates complete production-shaped browser-impact evidence using existing project runtime and browser-testing infrastructure.
classification: technical
opencode_permission:
  read:
    "/tmp/**": allow
  external_directory:
    "/tmp/**": allow
  skill:
    browser-visual-capture: allow
    browser-visual-compare: allow
inputs:
  - approved browser-impact contract and dependency-closure evidence
  - caller-provided permitted baseline capture paths under /tmp
  - affected actor route state and deterministic scenario matrix
  - project-native production build server and state lifecycle evidence
  - completed frontend behavior and accessibility evidence
  - caller-provided post-change capture and comparison paths under /tmp
---

# Frontend impact validation

## Inputs

Require an approved browser-impact contract and dependency-closure evidence, caller-provided permitted baseline capture paths under `/tmp`, an affected actor, route, state, and deterministic scenario matrix, project-native production build, server, and state-lifecycle evidence, completed frontend behavior and accessibility evidence, and caller-provided post-change capture and comparison paths under `/tmp`.

This skill is the browser-impact completion authority. It orchestrates existing adapters and project-native infrastructure; it does not create a browser runner, application server, fixture system, or custom command-line application.

## Deterministic workflow

```yaml
request: "Complete browser-impact gate result"
workflow:
  - id: post-change-capture
    when: "After implementation when baseline evidence and a deterministic runnable candidate scenario exist."
    skill: browser-visual-capture
  - id: visual-comparison
    when: "After comparable baseline and post-change artifacts exist for every affected scenario."
    skill: browser-visual-compare
```

## Procedure

1. Verify dependency closure rather than changed-file location. Every directly or indirectly affected actor, production route, and state must map to one exact deterministic scenario and approved expected outcome.
2. Verify baseline evidence was captured before implementation from production-shaped routes and compiled assets using the same viewport, state, actor, URL set, and run identity required for the candidate.
3. Verify the project-native build, server, and state lifecycle are documented and safe. When deterministic database state is required, require evidence from the separately selected shared database-fixture procedure. Missing runtime or lifecycle evidence is `blocked`.
4. Load `browser-visual-capture` for post-change diagnostic capture. Reject source-only fixtures, static mock routes, arbitrary waits, stale artifacts, or scenarios that cannot reproduce the approved state.
5. Load `browser-visual-compare` only for comparable pairs. Completion manifests must reject generic percentage-threshold acceptance, require zero differences in protected regions, explain every permitted changed region, and require zero unexplained differences outside it.
6. Require completed project-native behavior evidence and nonvisual accessibility evidence for every affected scenario. Screenshots and selectors do not substitute for interaction, recovery, keyboard, focus, status, or semantic assertions.
7. Verify all servers, browser processes, fixture targets, and temporary resources were stopped, destroyed, or safely quarantined. Verify evidence contains no credentials, secret-bearing URLs, raw sensitive payloads, or unsafe diagnostics.
8. Return `passed` only when every scenario has fresh comparable evidence, expected behavior, accessibility evidence, acceptable exact visual results, secret safety, and confirmed teardown. Return `failed` for explained assertion failures, `inconclusive` for missing or non-comparable evidence, and `blocked` for unavailable or unsafe infrastructure.
9. Mark evidence publishable only for `passed`. Report scenario coverage, artifact paths, comparison result, behavior and accessibility evidence, teardown, and blockers.

## Compatible foundations

Projects may use existing freely available browser infrastructure such as Playwright, Selenium, WebdriverIO, Cypress, Chromium, or framework-native browser tests. Prefer an established project harness. If adding one is separately approved, expose it through existing project validation commands rather than inventing another orchestration CLI.

## Audit criterion

A browser-impact change is nonconforming when dependency closure, production-shaped fresh baseline and candidate evidence, exact deterministic scenarios, behavior, nonvisual accessibility, zero unexplained or protected visual differences, secret safety, or teardown evidence is absent.
