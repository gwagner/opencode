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

1. Inventory all requirement files.
2. Treat them as overlapping descriptions of one product.
3. Identify authoritative language, examples, and acceptance criteria.
4. Reconcile duplicates and contradictions.
5. Extract product goals, actors, workflows, business rules, data needs, integrations, and constraints.
6. Record missing information necessary for implementation.
7. Ask concise clarifying questions only when ambiguity is critical and cannot be safely isolated.
8. Otherwise make the narrowest reasonable assumption and proceed.

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
