---
name: deterministic-skill-tree-authoring
description: Designs concise, recursive skill and agent workflows with explicit ordering, choices, and completion gates.
---

# Deterministic workflow authoring

Model an agent as one flat, ordered `workflow` list. A listed skill or agent owns its own procedure and may expose its own ordered workflow; those references form the recursive tree. Do not hide sequencing behind `primary`, `before`, or `dependencies`.

1. Define the agent's one final output and role boundary.
2. List each stage in execution order. Give every stage one exact trigger.
3. Use `skill` for a reusable procedure, `agent` for a delegated role, and `ask` for a human gate. A step has exactly one of these outcomes.
4. Use `select` only where one mutually exclusive outcome must be chosen. Its branches are ordered and exhaustive; each has exactly one `skill` or `agent` outcome.
5. A code-editing workflow ends its validation sequence with `project-validation` after every selected post-change procedure. A separately authorized commit stage may follow. Report `passed`, `failed`, `skipped`, or `blocked`.
6. Verify every skill identity, agent identity, permission, required Markdown reference, and direct/transitive workflow edge. Reject cycles, eager loading, prose-only loads, and parallel editing in one worktree.
7. Keep skills cohesive. Extract a distinct reusable procedure; otherwise retain it as a stage in its owning agent.

## Canonical format

```yaml
request: "<final output>"
workflow:
  - id: "<unique-stage-id>"
    when: "<exact trigger>"
    skill: "exact-skill-name"
  - id: "<decision-stage-id>"
    when: "<exact trigger>"
    repeat_until: "<explicit terminal condition>"
    select:
      question: "<what outcome is needed?>"
      precedence: "Evaluate branches in listed order; the final branch is fallback."
      branches:
        - when: "<exclusive trigger>"
          agent: "exact-agent-name"
        - when: "otherwise"
          skill: "exact-skill-name"
  - id: "validation"
    when: "After all selected post-change stages."
    skill: "project-validation"
    report: ["passed", "failed", "skipped", "blocked"]
```

- `workflow` is strictly sequential. A conditionally skipped step does not reorder later steps.
- `id`, `when`, and exactly one `skill`, `agent`, `ask`, or `select` are required for each step.
- `select` branches use exact identities and contain exactly one `skill` or `agent`.
- `repeat_until` is optional and allowed only on a `select` stage. It makes a loop explicit and states its terminal condition.
- Repeat a skill only for separate named stages, such as baseline and post-change capture.
- A skill or agent named in a workflow must itself expose its relevant ordered procedure; follow those edges to detect recursive loops.
- Agent prose may clarify a listed stage but cannot add a skill load or agent handoff absent from the workflow.

## Pre-use verification

Immediately before every skill or agent stage, verify:

1. identity resolves;
2. caller permission permits it;
3. required Markdown references resolve;
4. it is loaded or delegated immediately before use; and
5. no cycle, eager use, prose-only use, or concurrent worktree edit exists.

## Review output

Report retained role, extracted procedures, the YAML workflow, identity and permission checks, recursive-edge checks, completion-gate status, and blockers.
