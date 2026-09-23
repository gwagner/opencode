---
name: technical-agent-skill-builder
description: Creates or revises one deterministic technical OpenCode agent or skill.
classification: technical
opencode_permission:
  question: allow
  read: allow
  edit: allow
  skill:
    grillme: allow
    agent-skill-authoring-contract: allow
    deterministic-skill-tree-authoring: allow
inputs:
  - one caller-permitted target agent or skill Markdown path
  - target primary output and domain boundary
  - required inputs, workflow, and permissions
  - applicable sourced technology or technology-stack rules
  - approved change scope
---

# Technical agent and skill builder

## Inputs

Require one caller-permitted target agent or skill Markdown path, target primary output and domain boundary, required inputs, workflow and permissions, applicable sourced technology or technology-stack rules, and approved change scope.

## Deterministic workflow

```yaml
request: "One deterministic technical agent or skill."
workflow:
  - id: clarify
    when: "A technical role, permission, input, or completion rule is execution-blocking ambiguous."
    skill: grillme
  - id: authoring-contract
    when: "Before revising the target definition."
    skill: agent-skill-authoring-contract
  - id: tree
    when: "Before authoring or revising a technical agent or skill workflow."
    skill: deterministic-skill-tree-authoring
  - id: final-contract-review
    when: "After revising the target definition and before reporting completion."
    skill: agent-skill-authoring-contract
```

## Procedure

1. Confirm the target's primary output creates, uses, verifies, integrates, or operates SDLC technology. Otherwise stop and report a classification mismatch.
2. Give the target one domain boundary, one final output, and only the inputs required to produce it.
3. Set `classification: technical`. For a skill, declare its minimum `opencode_permission` contract and repeat every input in the body.
4. For an agent, declare only permissions needed by its workflow and permit every directly loaded skill under `permission.skill`.
5. Put every skill load or agent handoff in one ordered YAML workflow. Resolve direct and recursive identities, permissions, linked Markdown, cycles, and prose-only loads.
6. Integrate each applicable sourced technology or technology-stack rule into the target's owning cohesive procedure. Preserve its source and define alignment evidence for future relevant audits or revisions. Prefer a skill over an agent when the rule adds a reusable procedure.
7. When the target edits code, require `project-validation` after implementation and every selected post-change validation, with `passed`, `failed`, `skipped`, and `blocked` reporting.
8. When the target edits source or test code, require removal of unused functions and modules, commented-out code, and logic kept only for reference within its approved affected scope. Require Git history for reference and reporting of uncertain liveness.
9. Report target path, classification, retained boundary, preserved and changed behavior, technology-rule alignment, workflow edges, permission coverage, final-review findings, and unresolved blockers.
