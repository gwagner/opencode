---
name: evidence-traceability
description: Adds stable source citations, confidence, status classification, and traceability matrices to application specifications.
compatibility: opencode
metadata:
  domain: specification-quality
---

# Evidence and traceability

Use this skill for all substantial specification work.

## Source references

Use stable references whenever possible:

- `evidence:internal/http/routes.go#RegisterRoutes`
- `evidence:internal/service/lead.go#Qualify`
- `evidence:migrations/004_create_opportunities.sql`
- `evidence:web/components/lead-detail.ts#LeadDetail`
- `requirements:requirements/inbound-leads.md#lead-capture`

Prefer repository-relative paths and symbols over line numbers. Add line ranges only when stable and useful.

## Confidence

Assign confidence to important conclusions:

- **High**: Multiple strong, consistent sources.
- **Medium**: One strong source or several consistent weaker sources.
- **Low**: Naming, comments, placeholders, incomplete scaffolding, or indirect inference.

Confidence never replaces evidence.

## Traceability matrix

Include:

| Specification ID | Capability | Classification | Primary source | Supporting source | Confidence | Notes |
|---|---|---|---|---|---|---|

For forward specifications, classification normally describes requirement provenance.

For reverse-engineered specifications, classification normally describes implementation status.

## Discipline

- Trace material claims, not every sentence.
- Never cite an unrelated file merely because it contains similar terminology.
- Preserve conflicts rather than hiding them.
- Distinguish source fact from architectural inference.
- Identify analysis boundaries, inaccessible systems, and unexecuted validation.
