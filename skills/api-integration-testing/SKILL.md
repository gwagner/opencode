---
name: api-integration-testing
description: Builds maintainable API integration tests using existing project infrastructure for contracts, access control, validation, CRUD flows, and isolation.
compatibility: opencode
metadata:
  domain: api-testing
  phase: implementation
---

# API integration testing

Use after `api-discovery` establishes the endpoint contract and authentication model.

## Implementation

1. Reuse the project's test framework, location, client, fixtures, configuration, formatting, and lint conventions. Introduce no competing framework.
2. Cover the relevant baseline:
   - Public: unauthenticated success.
   - Authenticated: missing and invalid credentials rejected; valid credentials succeed.
   - Authorized: unauthenticated and authenticated-unauthorized requests rejected; authorized request succeeds.
3. Assert stable contract behavior: status, content type, required headers/fields/types, response schema, and documented error shape. Avoid volatile literals unless guaranteed.
4. Add prioritized negative cases for required fields, malformed values, enums, parameters, content types, and missing resources. Avoid combinatorial expansion before baseline coverage.
5. For CRUD, create unique test data, exercise the isolated lifecycle, verify effects, and clean up owned resources. Do not depend on arbitrary records or execution order.
6. Keep environment values configurable and reuse test-safe dependencies. Never embed credentials or redirect tests to production.
7. Extract helpers only when they remove meaningful repetition.

## Safe execution

Never truncate arbitrary data, drop schemas, delete unrelated records, modify production configuration, run destructive migrations, or mutate a production endpoint. If a safe target cannot be established, write useful tests, skip unsafe execution, and report the blocker.

Format and run the narrowest relevant tests incrementally, then broader integration checks when safe. Classify failures as test defect, implementation defect, contract mismatch, or environment blocker. Fix test defects; preserve meaningful failures and never change application behavior solely to make tests pass unless explicitly requested.
