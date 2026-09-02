---
name: api-auth-testing
description: Designs and implements API authentication, authorization, ownership, and tenant-boundary test matrices.
compatibility: opencode
metadata:
  domain: api-testing
  phase: authentication
---

# API authentication and authorization testing

Use when integration-testing APIs with access-control boundaries.

1. Determine the actual mechanism and documented behavior from specifications and implementation; do not invent authentication or assume status codes.
2. Acquire test credentials through existing fixtures/helpers, a documented endpoint, seeded identities, or environment-provided test credentials, in that order. Never hard-code real credentials.
3. Test public endpoints without credentials and, when useful, with valid credentials.
4. Test authenticated endpoints with no credentials, a practical invalid/expired credential, and a valid identity.
5. Test authorized endpoints unauthenticated, authenticated without required permission, and authenticated with permission.
6. Where applicable, prove a valid identity cannot access another user's, tenant's, administrator's, or out-of-scope resource. Prefer test-created resources.
7. Assert documented status and error shape, absence of protected data, and authentication headers when specified; never assert secret values.

Classify failures as test defect, contract mismatch, authentication defect, authorization defect, or environment/configuration blocker. Fix only test defects unless application changes were explicitly requested.
