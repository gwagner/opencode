---
name: security-operations
description: Reviews or specifies authentication, authorization, tenancy, privacy, audit, secrets, observability, deployment, migration, and operational behavior.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: security-operations
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: security-operations
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: security-operations
inputs:
  - security or operations scope
  - authority or observed evidence
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
