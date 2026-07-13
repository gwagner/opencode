---
name: security-operations
description: Reviews or specifies authentication, authorization, tenancy, privacy, audit, secrets, observability, deployment, migration, and operational behavior.
compatibility: opencode
metadata:
  domain: security-operations
---

# Security and operations

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

## Findings table

| Concern | Current or required behavior | Enforcement | Gap | Risk | Source |
|---|---|---|---|---|---|

Separate implemented controls, requirements, recommendations, and unknowns.
