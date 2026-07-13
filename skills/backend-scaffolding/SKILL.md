---
name: backend-scaffolder
description: Build backend application scaffolding from requirements and application specification infomration
---
### 1. Inspect the existing project

Before editing code, identify:

* Backend language and framework
* Package manager and build commands
* Existing directory structure
* Route and handler conventions
* Service or use-case patterns
* Repository and data-access patterns
* Validation and error-handling conventions
* Test, formatting, linting, and type-checking commands

Use existing project conventions whenever they are safe and usable.

Do not introduce a new architectural pattern when the existing structure already provides one.

### 2. Read targeted requirements

Use `/okf-reader` to locate the relevant:

* Features
* Workflows
* Entities
* API operations
* Validation rules
* Authorization rules
* Persistence requirements
* External integrations
* Error conditions

Do not read or summarize unrelated specification material.

Before editing, form an internal implementation map of:

* External entry points
* Business workflows
* Data boundaries
* Required types
* Known unknowns

Do not print this internal map unless a blocker requires explanation.

### 3. Map requirements to code

Create only the backend units supported by the specification:

* Routes, controllers, or handlers for external API operations
* Services or use cases for business workflows
* Repositories or data-access functions for persistence and external systems
* DTOs, schemas, or domain types for input and output boundaries
* Registration or dependency-wiring code required to make the scaffold reachable
* Focused tests when the existing project has an established testing pattern

Use domain terminology from the specification.

Do not invent generic abstractions that are not needed by the described feature.

### 4. Implement the scaffold

Each scaffolded operation should include, where applicable:

* Typed inputs
* Typed outputs
* Validation boundaries
* Explicit dependencies
* Expected error cases
* Repository or integration seams
* Route registration
* A useful implementation placeholder

Routes must remain thin. A route should:

1. Parse and validate transport input.
2. Call a service or use case.
3. Translate domain errors into transport responses.
4. Return a structured response.

Services must own workflow orchestration and must not depend on HTTP-specific behavior unless that is already the project convention.

Repositories must isolate persistence or external-system access and expose intention-revealing operations.

Prefer concrete functions and structs/classes over interfaces when there is only one trivial implementation.

Create an interface or protocol when at least one of these is true:

* It represents a real architectural boundary.
* The specification requires multiple implementations.
* The dependency must be replaced in tests.
* The existing project consistently models that boundary with interfaces.
* The implementation is not yet available and downstream code needs a stable contract.

Start from the public contract of a feature, then implement downward through service and data-access boundaries. Do not create speculative interface layers.

## Comment requirements

Comments are part of the scaffold and are required at incomplete implementation boundaries.

Add a comment or TODO when:

* Required behavior is intentionally deferred.
* A schema or field mapping is unknown.
* Credentials or integration details are unavailable.
* An authorization decision still needs implementation.
* A repository method cannot yet perform real persistence.
* An assumption was required because the specification was ambiguous.
* A failure mode still needs production handling.

Each deferred-work comment must explain:

1. Why the code is incomplete.
2. Which requirement or behavior it relates to.
3. What information or implementation is needed to complete it.

Use this format when a stable requirement or feature identifier exists:

```text
TODO(<requirement-id>): Explain the missing behavior and what is needed to implement it.
```

When no identifier exists, use:

```text
TODO(spec): Explain the missing behavior and what is needed to implement it.
```

Good example:

```text
// TODO(FEATURE-CALL-014): Persist the provider call ID after the telephony
// adapter contract and calls table fields are finalized.
```

Bad examples:

```text
// TODO: implement
// Call the service.
// This function creates a call.
```

Do not comment obvious syntax or restate function names.

Use doc comments only for:

* Public APIs
* Non-obvious contracts
* Important invariants
* Error semantics
* Deferred implementation boundaries

Prefer a precise comment in the code over a lengthy explanation in the final response.

## Placeholder rules

A placeholder must still be useful.

Do not create empty methods, silent no-ops, or misleading success responses.

When implementation cannot be completed:

* Define the intended contract.
* Validate what can already be validated.
* Return a typed not-implemented or integration-unavailable error.
* Add a requirement-linked TODO.
* Keep downstream code compilable whenever practical.

Never add:

* Fake credentials
* Fake production integrations
* Fabricated database results
* Random identifiers presented as real persisted values
* Success responses for operations that did not occur
* Speculative migrations unless explicitly requested

## File organization

Prefer the existing project structure.

Keep closely related code together when the project is small or the behavior is simple.

Split code into additional files only when it improves an existing architectural boundary or prevents a file from mixing unrelated responsibilities.

Do not centralize unrelated concepts merely to reduce the number of files.

Do not reformat or refactor unrelated code.

## Error handling

Model only relevant failures, including:

* Invalid input
* Not found
* Unauthorized or forbidden
* Conflict
* Persistence failure
* External integration failure
* Unexpected internal failure

Do not add every possible error branch to every function.

Use the project’s existing error types and response conventions when available.

Do not swallow errors.

## Validation

After modifying code, run the narrowest practical checks supported by the project, such as:

* Formatter
* Compiler or build
* Type checker
* Linter
* Targeted unit tests
* Package-level tests

Fix errors caused by your changes.

Do not perform broad unrelated cleanup merely to make a repository-wide check pass.

If validation cannot run, state the exact reason briefly.

## Completion criteria

Before finishing, verify that:

* Every new route is registered or clearly marked for registration.
* Every route calls a real service or use-case boundary.
* Every service dependency is supplied or wired consistently with the project.
* Every incomplete boundary has a meaningful TODO comment.
* New public contracts have appropriate documentation.
* Placeholder code does not pretend that work succeeded.
* Imports, exports, names, and types are consistent.
* The code builds or is as close to buildable as missing project information permits.
* No unrelated files were changed.

## Final response

Keep the final response concise.

Use no more than these four sections:

### Changed

List the files created or modified and the main backend capabilities added.

### Specification used

List only the specification, feature, or requirement identifiers that directly informed the changes.

### Validation

List commands run and whether they passed.

### Remaining

List only unresolved assumptions, blockers, and important TODOs.

Do not include:

* A step-by-step narration
* A long architecture explanation
* Repeated summaries of code visible in the diff
* Generic recommendations
* Large code excerpts
* Praise for your own implementation

If the required paths cannot be accessed or no usable requirements are found, do not invent code. State the missing inputs and stop.

