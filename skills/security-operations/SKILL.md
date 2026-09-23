---
name: security-operations
description: Reviews or specifies authentication, authorization, tenancy, privacy, audit, secrets, observability, deployment, migration, and operational behavior.
classification: non-technical
opencode_permission:
  read: allow
inputs:
  - security or operations scope
  - caller-provided permitted authority source configuration and observed evidence paths
compatibility: opencode
metadata:
  domain: security-operations
---

# Security and operations

## Inputs

Require a security or operations scope and caller-provided permitted authority, source, configuration, and observed evidence paths.

## Security review

Inspect or define:

- Authentication
- Session or token handling
- Authorization enforcement
- Role and resource checks
- Tenant isolation
- Secret loading and rotation
- Input validation
- SQL injection resistance
- Output encoding
- Webhook signature verification
- CSRF and CORS behavior where relevant
- Sensitive-data handling
- Transcript and personal-data handling
- Audit events
- Retention and deletion
- Administrative overrides

Do not claim compliance certification without authoritative evidence.

## Operational specification

Document:

- Build artifacts
- Runtime services
- Containers
- Environment variables
- Database provisioning
- Migration execution
- Startup and shutdown
- Health and readiness checks
- Logging
- Metrics
- Tracing
- Alerting
- Backup and recovery
- Scaling assumptions
- Scheduled jobs
- Failure recovery

## Logging requirements

Specify every emitted log event with a UTC timestamp, stable event code, severity, owning component, operation, and outcome. When the event context contains them, include the environment, build or release version, runtime instance, request or correlation identifier, trace and span identifiers, safe subject identifiers, dependency or adapter, attempt number, duration, error class, retryability, parent or cause event code, and non-secret configuration revision. Optional fields MUST be omitted rather than populated with fabricated or ambiguous values. Runtime-instance and correlation fields MAY be high-cardinality log fields but MUST NOT become metric labels.

Assign severity by the first matching row, in listed order:

| Severity | Required use |
|---|---|
| `ERROR` | The current operation failed and its owning boundary cannot complete it successfully. |
| `WARN` | The operation completed or recovered, but an approved anomaly threshold was breached or an approved degraded-mode fallback was used. |
| `INFO` | An approved lifecycle, business, security, or operational state transition completed. Routine per-request progress MUST NOT be `INFO` unless explicitly required. |
| `DEBUG` | Bounded internal diagnostic detail useful for investigation but unnecessary for normal operation. |
| `TRACE` | High-volume step-level diagnostic detail explicitly approved for a bounded investigation. |

The boundary that handles, converts, or terminates a failure MUST own its error log. Lower layers MUST return typed or wrapped errors without logging the same failure unless they own a distinct observable event that cannot be represented to the caller. Expected validation, not-found, conflict, caller-cancellation, and authorization outcomes MUST NOT be `ERROR`; omit them unless an approved business, security, or audit requirement needs an event, then use `INFO` or `WARN` according to the table. They MUST NOT include stack traces merely because they are represented as errors. An internal timeout or cancellation that prevents completion is `ERROR` at the owning boundary.

Unexpected internal failures MAY include a stack trace only in protected internal logs. Production-facing responses, public diagnostics, metrics, and audit records MUST NOT contain stack traces or internal error text. `DEBUG` and `TRACE` MUST be disabled in production by default; temporary production enablement MUST be scoped by component or correlation identifier, time-bounded, access-controlled, and auditable.

Redact before emission. Logs MUST NOT contain credentials, tokens, session identifiers, cryptographic material, secret-bearing URLs, raw personal or regulated data, or complete request and response bodies unless an authoritative requirement explicitly approves named fields. Provider and internal errors MUST be mapped to stable safe classes. Variable text, collections, payload excerpts, and stack traces MUST have explicit size limits and truncation markers.

Specify bounded sampling or rate limiting for repeatable high-volume events while preserving a count of suppressed events. Use low-cardinality labels, distinguish expected no-work from anomalies, and prevent logging, export, or recorder failures from recursively emitting the same failure. User-visible error detail and internal log detail MUST be specified independently.

When end-user interactions exist, specify a named environment variable with allowlisted values and explicit deployment-environment mappings for interaction logging. A missing value MUST select diagnostic mode only in an explicitly identified development environment and production-business mode otherwise; an unsupported value MUST fail startup. Development MUST support an approved diagnostic mode that records bounded interaction lifecycle detail sufficient to reconstruct routes or surfaces, actions, state transitions, validation, failures, and recovery without recording prohibited data. Production MUST default to approved named business events and outcomes; routine clicks, keystrokes, field changes, raw inputs, payloads, and bodies MUST NOT be emitted. A production diagnostic override MUST be explicitly authorized, scoped by component or correlation identifier, time-bounded, access-controlled, auditable on activation and deactivation, and automatically restored to the production default. The specification MUST define mode ownership, permitted events and fields, redaction, sampling or rate limits, retention, configuration validation, and tests for every supported environment mode and override transition.

For browser-originated interaction events, the backend MUST own the effective mode and event catalog and MUST treat every submitted field as untrusted. Require same-origin authenticated ingestion with applicable request protection, strict schema and size validation, event and field allowlists, rate limits, and bounded duplicate handling. The backend MUST discard client-provided severity, environment, tenant, subject identity, trusted timestamps, correlation context, and sink selection; redact before enrichment; add trusted request, session, tenant, correlation, environment, release, and receipt-time context only when available and permitted; then emit through the existing structured application logger. The browser MUST NOT write files, address a logging sink directly, block the user workflow on telemetry, retry without bounds, or expose ingestion failures to recursive logging. Deployment owns routing from the application logger to its approved file, standard-output, or collector sink and owns file permissions and rotation when a file sink is selected.

Logging requirements are complete only when every required event has an owner, trigger, severity, stable code, permitted fields, redaction rule, volume control, retention destination when governed by authority, and verification method. Failure events MUST provide enough approved context to identify the deployed version and reconstruct one request, job, or workflow across owning boundaries when that context exists. Otherwise record the item as a gap or unknown.

For startup and probes, specify mandatory initialization barriers, fail-closed startup, readiness recovery behavior, liveness independence when applicable, minimal snapshot-only public responses, no dependency work per probe, and structural exclusion of test or development capabilities from production composition, routes, artifacts, and commands.

## Findings table

| Concern | Current or required behavior | Enforcement | Gap | Risk | Source |
|---|---|---|---|---|---|

Separate implemented controls, requirements, recommendations, and unknowns.
