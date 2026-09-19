---
name: requirements-analysis
description: Analyzes raw product requirements into explicit requirements, implications, assumptions, constraints, ambiguities, and traceable specification inputs.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: requirements-analysis
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: requirements-analysis
    - agent: prd-strategist
      source: /code/agents/prd-strategist.md
      allowed_skill: requirements-analysis
    - agent: todo-planner
      source: /code/agents/todo-planner.md
      allowed_skill: requirements-analysis
inputs:
  - requirements scope
  - accessible requirements bundle
compatibility: opencode
metadata:
  direction: requirements-to-specification
---

# Requirements analysis

## Deterministic workflow

```yaml
request: "Traceable analysis of raw product requirements"
workflow:
  - id: "retrieve-requirement-knowledge"
    when: "For a scoped question in a large requirements bundle."
    skill: "okf-reader"
```

Use this skill when the primary source is `/project/requirements/`.

## Procedure

1. Inventory paths, indexes, and concept frontmatter; do not load every body by default.
2. For a scoped question in a large bundle, use the `okf-reader` retrieval workflow to select bounded sections, then read their necessary context.
3. Treat selected requirements as overlapping descriptions of one product. Expand the reading set only when links, duplicate candidates, or possible conflicts require it.
4. Identify authoritative language, examples, and acceptance criteria.
5. Reconcile duplicates and contradictions.
6. Extract product goals, actors, workflows, business rules, data needs, integrations, and constraints.
7. Record missing information necessary for implementation.
8. Ask concise clarifying questions only when ambiguity is critical and cannot be safely isolated.
9. Otherwise make the narrowest reasonable assumption and proceed.

## Classification

Classify findings as:

- **Explicit requirement**
- **Implied requirement**
- **Necessary assumption**
- **Open question**
- **Conflict**
- **Out of scope**

Do not silently promote implied behavior into explicit requirements.

## Traceability

Give important requirements stable IDs.

Link specification content to requirement evidence using forms such as:

- `requirements:requirements/inbound-leads.md#lead-capture`
- `requirements:requirements/reporting.md#conversion-dashboard`

When headings are unavailable, reference the file and a concise locator.

## Conflict handling

When requirements conflict:

1. Show the conflicting statements.
2. Determine whether scope, actor, or lifecycle context resolves the conflict.
3. Prefer more specific language over general language.
4. Prefer explicit acceptance criteria over examples.
5. Preserve unresolved conflicts as open questions.
