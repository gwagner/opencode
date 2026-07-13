---
name: spec-driven-implementation
description: Implements code changes required to align a codebase with an authoritative application specification, including tests, migrations, validation, and regenerated code-derived documentation.
compatibility: opencode
metadata:
  domain: implementation
---

# Specification-driven implementation

Use this skill after `specification-reconciliation` has identified confirmed gaps.

## Source-of-truth policy

- `/project/specification/` defines required behavior.
- `/code/specification/` describes current behavior.
- `/code/specification/reconciliation-report.md` tracks differences.
- Production code under `/code/` is the implementation target.

Never alter `/project/specification/` merely to match existing code.

## Implementation sequence

For each gap:

1. Read the authoritative requirement.
2. Inspect the complete affected vertical slice.
3. Identify the smallest coherent code change.
4. Update domain behavior first.
5. Update persistence and migrations when needed.
6. Update API, integration, and frontend layers.
7. Add or update tests.
8. Run focused validation.
9. Run broader regression validation when safe.
10. Regenerate `/code/specification/`.
11. Re-run reconciliation.
12. Mark the gap resolved only if the regenerated specification aligns.

## Change discipline

- Prefer behavior-preserving refactors only when required for the gap.
- Do not bundle unrelated cleanup.
- Do not invent product behavior beyond the authoritative specification.
- Preserve backward compatibility unless the authoritative specification requires a breaking change.
- Make database changes forward-safe and reversible where practical.
- Use idempotent migration and webhook patterns.
- Preserve tenant isolation, auditability, and transaction boundaries.
- Add tests that demonstrate the authoritative behavior, not merely implementation details.

## Extra implementation

When code contains behavior absent from the authoritative specification:

- Do not automatically delete it.
- Determine whether it conflicts with required behavior.
- If conflicting, remove or disable it.
- If harmless but externally visible, flag it for product review.
- If internal and harmless, document it as extra implementation.

## Validation record

For each resolved gap record:

- Files changed
- Tests added or updated
- Commands executed
- Results
- Migration impact
- API or UI impact
- Updated code-derived evidence
