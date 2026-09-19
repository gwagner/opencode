---
name: api-discovery
description: Discovers intended API contracts, implemented routes, access control, mismatches, and reusable test infrastructure before API integration testing.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: api-integration-tester
      source: /code/agents/api-integration-tester.md
      allowed_skill: api-discovery
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: api-discovery
inputs:
  - API scope
  - authority sources
  - application and test source locations
compatibility: opencode
metadata:
  domain: api-testing
  phase: discovery
---

# API discovery

Use before creating API integration tests. Compare the caller-provided specification and source locations; do not assume fixed paths.

1. Inspect OpenAPI/Swagger files, endpoint documentation, requirements, acceptance criteria, authentication rules, and examples.
2. Inspect startup and route wiring, handlers, middleware, request/response models, authentication and authorization enforcement, configuration, dependencies, and existing integration-test helpers.
3. For each endpoint record method, path, source evidence, parameters, headers, body, response schema, success/errors, and role/scope/ownership rules.
4. Classify access as `PUBLIC`, `AUTHENTICATED`, `AUTHORIZED`, or `UNKNOWN`; never infer access from naming alone.
5. Compare intended and implemented method, route, fields, statuses, and access rules. Preserve both sides of every mismatch; implementation evidence does not override the contract.
6. Identify the existing framework, startup mechanism, test runner, clients, fixtures, factories, containers, authentication helpers, and—when relevant—PostgreSQL test-target resolution, including whether project wiring consumes `DATABASE_URL` or `POSTGRES_PASSWORD`. Never disclose environment values. Prefer project conventions over new infrastructure.

Return application/test infrastructure, authentication mechanisms and credential acquisition, PostgreSQL target-resolution evidence when relevant, a `METHOD PATH | classification | expected success | implementation status` inventory, and explicit specification mismatches. Include enough path/symbol evidence for test implementation without rediscovery.
