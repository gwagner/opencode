---
name: specification-reconciliation
description: Compares an authoritative application specification with a code-derived specification, identifies behavioral and structural gaps, and creates a traceable reconciliation plan.
compatibility: opencode
metadata:
  domain: specification-reconciliation
---

# Specification reconciliation

Use this skill to compare:

- Authoritative specification: `/project/specification/`
- Code-derived specification: `/code/specification/`

The authoritative specification always wins unless the user explicitly changes that policy.

## Inputs

Read both specification trees using `okf-reader`.

Treat `/project/specification/` as the required product behavior.

Treat `/code/specification/` as a description of current implementation behavior, not as a competing source of truth.

## Comparison model

Compare by capability rather than by document paragraph.

Build a normalized inventory of:

- Product goals
- Actors and permissions
- Functional requirements
- Workflows
- Lifecycle states and transitions
- Entities and fields
- Database constraints
- API endpoints and contracts
- Webhooks and integrations
- Frontend routes and components
- Validation and errors
- Security controls
- Audit behavior
- Operational behavior

## Gap classifications

Classify every material comparison as one of:

- **Aligned**: Code-derived behavior satisfies the authoritative specification.
- **Missing in code**: Required behavior is absent.
- **Partially implemented**: Some required behavior exists but is incomplete.
- **Behavioral divergence**: Code behavior contradicts the authoritative specification.
- **Contract divergence**: API, event, schema, or UI contract differs.
- **Data-model divergence**: Entity, field, relationship, constraint, or lifecycle differs.
- **Security divergence**: Required authentication, authorization, privacy, or audit behavior is missing or different.
- **Extra implementation**: Code contains behavior not described by the authoritative specification.
- **Ambiguous implementation**: Available code-derived evidence cannot establish actual behavior.
- **Specification ambiguity**: The authoritative specification contains contradictory or insufficient instructions.

Do not treat extra implementation as correct merely because it exists.

Do not modify `/project/specification/` to make a difference disappear.

## Reconciliation report

Write the report to:

`/code/specification/reconciliation-report.md`

Use this table:

| Gap ID | Capability | Classification | Authoritative requirement | Current code-derived behavior | Required code change | Validation | Priority | Status |
|---|---|---|---|---|---|---|---|---|

Use stable gap identifiers such as:

- `GAP-AUTH-001`
- `GAP-LEAD-001`
- `GAP-API-001`
- `GAP-DATA-001`

## Prioritization

Use:

- **P0**: Security, data corruption, tenant isolation, or externally breaking behavior.
- **P1**: Core workflow or required state transition is absent or wrong.
- **P2**: Important but non-blocking behavior, reporting, recovery, or UI gap.
- **P3**: Low-risk inconsistency, cleanup, or undocumented extra behavior.

## Ambiguity handling

When implementation understanding is incomplete:

1. Inspect the actual code, tests, migrations, routes, and runtime wiring.
2. Update `/code/specification/` with better implementation evidence.
3. Re-run the comparison.
4. If ambiguity remains, record it as `Ambiguous implementation`.
5. Do not guess that the code is compliant.

When the authoritative specification itself is ambiguous:

1. Record `Specification ambiguity`.
2. Do not modify `/project/specification/`.
3. Do not make a speculative product decision in code.
4. Isolate the ambiguity and continue with unaffected gaps.

## Completion criteria

A gap is resolved only when:

- Production code has been updated.
- Relevant tests have been added or updated.
- Migrations or contracts have been updated when required.
- Validation commands pass.
- `/code/specification/` has been regenerated from the updated code.
- The regenerated code-derived specification now aligns with `/project/specification/`.
- The gap row is marked resolved with evidence.
