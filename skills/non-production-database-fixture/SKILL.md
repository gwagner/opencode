---
name: non-production-database-fixture
description: Verifies and executes one deterministic database-backed test through an existing project-native isolated fixture lifecycle.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  skill:
    project-validation: allow
inputs:
  - approved deterministic database-state contract
  - caller-provided permitted fixture configuration source and test paths
  - existing project-native fixture lifecycle
  - project-native validation context and permitted command set
---

# Non-production database fixture

## Inputs

Require an approved deterministic database-state contract, caller-provided permitted fixture configuration, source, and test paths, an existing project-native fixture lifecycle, and project-native validation context and permitted command set.

This skill verifies and uses existing project infrastructure. It never creates a new fixture framework, command-line application, connection convention, migration runner, seed system, or cleanup mechanism.

## Deterministic workflow

```yaml
request: "Safely executed deterministic database-backed test lifecycle"
workflow:
  - id: validate-project
    when: "After fixture lifecycle checks establish a safe project-native target."
    skill: project-validation
    report:
      - passed
      - failed
      - skipped
      - blocked
```

## Procedure

1. Inspect only the caller-permitted project fixture configuration, test helpers, validation guidance, and lifecycle implementation. Identify one lifecycle owner and the exact existing project-native validation command that consumes it.
2. Require explicit non-production mode, fresh whole-database ownership, an opaque lease or equivalent ownership attestation, current migrations, deterministic state composition, and test-only identities and clocks when needed.
3. Require application state to be composed through production interfaces or established project adapters. Deny every reachable email, webhook, payment, cloud, network, or other external effect through existing test adapters.
4. Require the lifecycle owner to perform cleanup only for its attested target. Uncertain ownership or cleanup must quarantine the target or return `blocked`; it must never guess, truncate shared state, or destroy an unattested database.
5. Require each retry to use a wholly new target, lease, session, and identity set. Do not reuse failed or uncertain state.
6. Use `project-validation` to run only the established project-native command. Do not construct connection strings, override inherited target configuration, invoke database-native destructive commands, or add a competing provisioner.
7. Report lifecycle owner, target-isolation evidence, migration and state-composition evidence, external-effect denial, exact command, outcome, teardown or quarantine evidence, and blockers. Never report credentials or connection details.

## Compatible foundations

Projects may implement the lifecycle with existing freely available infrastructure such as Docker or Podman containers, Docker Compose, Testcontainers, framework-native isolated test databases, or CI service containers. This skill does not install, configure, or invoke those tools directly; the project-native lifecycle owns them.

## Audit criterion

A database-backed feature test is nonconforming when it uses ad hoc allocation, connection construction, migration, seeding, clock, identity, reset, cleanup, shared mutable state, or reachable external effects instead of one attested project-native lifecycle.
