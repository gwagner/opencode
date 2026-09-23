---
name: api-discovery
description: Discovers intended API contracts, implemented routes, access control, mismatches, and reusable test infrastructure before API integration testing.
classification: non-technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
inputs:
  - API scope
  - caller-provided permitted authority application and test source paths
compatibility: opencode
metadata:
  domain: api-testing
  phase: discovery
---

# API discovery

## Inputs

Require API scope and caller-provided permitted authority, application, and test source paths.

Use before creating API integration tests. Compare the caller-provided specification and source locations; do not assume fixed paths.

1. Inspect OpenAPI/Swagger files, endpoint documentation, requirements, acceptance criteria, authentication rules, and examples.
2. Inspect startup and route wiring, handlers, middleware, request/response models, authentication and authorization enforcement, configuration, dependencies, and existing integration-test helpers.
3. For each endpoint record method, path, source evidence, parameters, headers, body, explicit response-field allowlist, null/unavailable semantics, success/errors, read-versus-command classification, domain and external effects, and role/scope/ownership rules.
4. Classify access as `PUBLIC`, `AUTHENTICATED`, `AUTHORIZED`, or `UNKNOWN`; never infer access from naming alone.
5. For tenant-owned or nested resources, record the authenticated source of tenant scope, first tenant-scoped data access, parent/child/subtype/channel ownership graph, and approved equivalent safe-absence behavior for unknown and mismatched identifiers.
6. For external integrations, record explicit credential provenance, prohibited ambient fallback, event-time snapshot fields, stable retry identity, and redaction boundary when authority defines them.
7. Compare intended and implemented method, route, fields, statuses, semantic values, effects, and access rules. Preserve both sides of every mismatch; implementation evidence does not override the contract.
8. Identify the existing framework, startup mechanism, test runner, clients, fixtures, factories, containers, authentication helpers, and relevant safe test-target lifecycle. Never disclose environment values or infer connection settings. Prefer approved shared infrastructure over feature-owned provisioning.

Return application/test infrastructure, authentication and tenant-source evidence, safe target-lifecycle evidence, ownership graph, a `METHOD PATH | access | read-or-command | expected success | implementation status` inventory, and explicit specification mismatches. Include enough path/symbol evidence for test implementation without rediscovery.
