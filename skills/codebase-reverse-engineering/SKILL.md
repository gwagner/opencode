---
name: codebase-reverse-engineering
description: Reverse-engineers product behavior and architecture from source code, migrations, tests, configuration, interfaces, frontend code, and runtime wiring.
compatibility: opencode
metadata:
  direction: code-to-specification
---

# Codebase reverse engineering

Use this skill when reconstructing an application specification from an existing repository.

## Repository inventory

Inspect strategically:

- Repository instructions such as `AGENTS.md`
- Entry points and executable applications
- Dependency manifests
- Routes and interface registration
- Handlers, controllers, and middleware
- Domain models and services
- Repository interfaces and concrete implementations
- Database migrations and schema definitions
- Frontend routes and components
- Tests, fixtures, mocks, and test data
- API schemas
- External integration clients
- Configuration and environment variables
- Background jobs and workers
- Deployment files
- Existing requirements and specifications
- Git history when it materially clarifies intent

Exclude generated output, caches, vendor directories, and build artifacts unless they define an external contract.

## Evidence hierarchy

Resolve conflicts using this order:

1. Executable behavior and tests
2. Database migrations and persisted constraints
3. External API schemas and contracts
4. Domain and service logic
5. Handlers, controllers, and UI behavior
6. Runtime wiring and configuration
7. Current documentation
8. Comments and TODOs
9. Naming-based inference

## Classification

Classify major findings as:

- **Implemented**
- **Partially implemented**
- **Declared**
- **Inferred**
- **Expected but absent**
- **Unknown**
- **Conflicting**

Examples:

- An interface without a wired concrete implementation is declared.
- A route returning placeholder data is partially implemented.
- A migration proves persistence structure, not a complete product workflow.
- A generated client does not prove the integration is used.
- A config key does not prove the feature is operational.
- A TODO expresses intent, not behavior.
- A state constant is not necessarily reachable.
- An endpoint is not operational unless registered through an executable path.

## Vertical-slice tracing

For each major capability, trace:

1. User action or external event
2. Frontend or caller
3. Route, RPC, webhook, or job
4. Validation
5. Handler
6. Domain or service behavior
7. Persistence
8. Events and side effects
9. Response or UI state
10. Tests

Prefer vertical slices over file-by-file descriptions.

## Runtime verification

When safe and available:

- Inspect dependency construction.
- Confirm route reachability.
- Inspect migrations in execution order.
- Run focused tests.
- Run static analysis or project-native validation.
- Verify state transitions and database constraints.
- Record failed or unavailable checks as confidence limitations.
