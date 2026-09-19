---
name: deterministic-skill-tree-authoring
description: Designs deterministic, focused skill-use trees for OpenCode agents. Use when auditing or revising an agent's skill-use workflow, triggers, dependencies, or skill permissions.
---

# Deterministic skill-use-tree authoring

Create an agent-local skill-use tree; do not route the current user request or combine independent skill procedures.

1. Identify the agent's one final-output domain and its workflow stages.
2. For each stage, select the narrowest current skill that owns its final output. Do not create a new skill unless no focused existing skill fits.
3. Define one mutually exclusive trigger for every primary-skill branch. Resolve overlaps with explicit precedence based on the requested final output.
4. Define conditional dependencies with an exact trigger and a sequential use position. A dependency refines or validates the primary procedure; it cannot duplicate or replace it.
5. Require one primary skill per request. Split requests with independently deliverable outcomes. Never direct parallel use, eager use, or an unordered list of optional skills.
6. For every skill use, verify its exact `name`, its permission in the agent frontmatter, and any referenced Markdown resolution. Add only the narrowest required permission.
7. Reject cycles, conflicting ordering rules, unrelated skills, and instructions that make an agent own another agent's domain.
8. Reconcile every skill-use instruction in agent prose with the tree: each used skill must have one tree position, exact trigger, and use order. Prose may clarify a tree path but cannot add an unmodeled use.
9. For a role that edits code, model a completion gate for every code change. Use `project-validation` after implementation and any selected post-change validation dependency, before reporting completion. Require its result to be reported as passed, failed, skipped, or blocked.
10. Never rely on description-triggered skill autoloading for a required workflow stage. A required skill must be explicitly named in the ordered skill-use tree and allowed by the agent's `permission.skill`; verify it immediately before its modeled use. Autoloading is convenience only, not deterministic wiring or completion evidence.

## Skill-use-tree format

Express every proposed or revised skill-use tree as one YAML document in a
fenced `yaml` block. YAML is the canonical workflow representation; do not
also provide an ASCII tree or an unordered skill list.

```yaml
request: "<request>"
decision:
  question: "<what final output is requested?>"
  precedence: "Evaluate branches in listed order; the final branch is fallback."
  branches:
    - when: "<exclusive trigger A>"
      primary:
        skill: "exact-skill-name"
        dependencies:
          - when: "<exact condition>"
            after: "primary"
            skill: "exact-skill-name"
    - when: "otherwise"
      primary:
        skill: "exact-skill-name"
```

- `branches` is an ordered list. Its triggers must be mutually exclusive after
  applying `precedence`, exhaustive, and evaluated in list order.
- Every branch has exactly one `primary`; use exact skill identities, never
  display names. Put conditional work only in that primary's `dependencies`.
- Each dependency must state `when`, `after: "primary"`, and `skill`; it may
  refine or validate the primary procedure but cannot replace or duplicate it.
- Include unavailable or unpermitted skills nowhere in the YAML. Report each
  as a blocker below it.
- For every code-editing primary, add a `completion` mapping after
  `dependencies` with `after: "all selected post-change dependencies"`,
  `skill: "project-validation"`, and
  `report: ["passed", "failed", "skipped", "blocked"]`. A no-runnable-check
  outcome is `skipped` or `blocked`, never an omitted gate.

## Pre-use verification list

Keep load timing out of the tree. For every modeled use, run and report this
ordered verification immediately before that use:

1. The exact skill identity resolves.
2. The agent's `permission.skill` permits the identity.
3. Every Markdown reference required by that use resolves.
4. The skill is loaded immediately before its modeled use.
5. No eager, parallel, or prose-only skill use bypasses the tree.

### YAML rules

- Use valid YAML with two-space indentation, no tabs, and quoted scalar values
  where punctuation could change YAML parsing.
- Keep `request`, `decision.question`, `decision.precedence`, `branches`,
  `when`, `primary`, `skill`, `dependencies`, `after`, `completion`, and
  `report` exactly as named above.
- Keep each `dependencies` and `completion` mapping nested under its owning
  `primary`; never represent either as a sibling branch.
- Do not use YAML aliases, merge keys, or implicit defaults. Every modeled
  skill use, trigger, ordering rule, and completion gate must be explicit.

### Pre-report verification

Before reporting a skill-use tree, manually verify all of the following:

1. The YAML parses and contains one `request`, one `decision`, and one ordered
   `branches` list.
2. Every branch has one primary skill; dependencies and completion gates are
   nested only under that primary.
3. Every displayed skill identity, trigger, condition, ordering rule, and
   completion gate matches the prose and ordered use workflow.
4. All primary branches are mutually exclusive and exhaustive in their stated
   evaluation order; dependencies appear only below their primary.

## Future-skill admission

Before adding, renaming, or retaining a skill use in a tree, require all of:

- one cohesive reusable procedure and one final output;
- a distinct trigger and boundary from existing skills;
- one declared primary-use or dependency-use position;
- no overlap that needs interpretation at runtime; and
- matching agent permission and resolvable identity.

Otherwise extract, merge, or remove the procedure rather than adding another branch.

## Required review output

Report the agent's retained role, extracted or removed procedures, the proposed
ordered skill-use tree using the Skill-use-tree format, the ordered pre-use
verification results, exact permission changes, and
unresolved ambiguity. Use `grillme` for ambiguity that prevents mutually
exclusive branches or a safe precedence rule.
