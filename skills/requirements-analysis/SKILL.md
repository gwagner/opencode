---
name: requirements-analysis
description: Analyzes raw product requirements into explicit requirements, implications, assumptions, constraints, ambiguities, and traceable specification inputs.
compatibility: opencode
metadata:
  direction: requirements-to-specification
---

# Requirements analysis

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
