---
name: api-auth-testing
description: Designs and implements API authentication, authorization, ownership, and tenant-boundary test matrices.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    non-production-database-fixture: allow
    project-validation: allow
inputs:
  - established API contract
  - access-control model
  - safe test credentials
  - caller-provided permitted API authority source and test paths
  - caller-provided permitted database fixture contract path when deterministic application state is required
compatibility: opencode
metadata:
  domain: api-testing
  phase: authentication
---

# API authentication and authorization testing

## Inputs

Require an established API contract, access-control model, safe test credentials, caller-provided permitted API authority, source, and test paths, and a caller-provided permitted database fixture contract path when deterministic application state is required.

## Dead-code rule

Within the approved affected test scope, remove unused test helpers and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in tests. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "API access-control test matrix and validation result"
workflow:
  - id: database-fixture
    when: "After access-control tests are implemented when execution requires deterministic application database state."
    skill: non-production-database-fixture
  - id: validate-project
    when: "After access-control test implementation and every selected post-change check."
    skill: project-validation
    report:
      - passed
      - failed
      - skipped
      - blocked
```

Use when integration-testing APIs with access-control boundaries.

1. Determine the actual mechanism and documented behavior from specifications and implementation; do not invent authentication or assume status codes.
2. Acquire test credentials through the approved shared test lifecycle, existing fixtures/helpers, a documented endpoint, or environment-provided test credentials, in that order. Do not create feature-owned identity or seeding paths, and never hard-code real credentials.
3. Test public endpoints without credentials and, when useful, with valid credentials.
4. Test authenticated endpoints with no credentials, a practical invalid/expired credential, and a valid identity.
5. Test authorized endpoints unauthenticated, authenticated without required permission, and authenticated with permission.
6. For tenant-owned or nested resources, record the authenticated source of tenant scope and test authorized success, unknown identifier, wrong tenant, mismatched parent and child, and wrong subtype or channel. Prefer test-created resources.
7. Assert every denial produces the approved equivalent safe-absence status, headers, and error shape without protected data, ownership hints, counts, extra repository reads, external calls, audits, or mutations.
8. Assert documented authentication headers when specified; never assert secret values.

Classify failures as test defect, contract mismatch, authentication defect, authorization defect, or environment/configuration blocker. Fix only test defects unless application changes were explicitly requested.
