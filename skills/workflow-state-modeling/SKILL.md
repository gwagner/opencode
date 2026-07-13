---
name: workflow-state-modeling
description: Designs or recovers explicit business workflows, lifecycle states, transition rules, funnels, audit events, and edge cases.
compatibility: opencode
metadata:
  domain: domain-modeling
---

# Workflow and state modeling

Use this skill whenever an application has lifecycle, approval, funnel, fulfillment, qualification, or status-driven behavior.

## Workflow specification

For each workflow define:

- Actor
- Entry condition
- Trigger
- Ordered steps
- Persisted changes
- Notifications or side effects
- Alternate paths
- Failure paths
- Completion criteria
- Audit requirements

## State model

Use this table:

| State | Meaning | Entry criteria | Allowed prior states | Allowed next states | Trigger | Required metadata | Side effects | Terminal or reversible | Source |
|---|---|---|---|---|---|---|---|---|---|

Also include a Mermaid state diagram when useful.

## Transition rules

Specify:

- Who may perform the transition
- Whether the transition is manual, automatic, or webhook-driven
- Required fields
- Validation
- Transaction boundaries
- Concurrent update behavior
- Audit event
- Reversal or reopening behavior
- Idempotency requirements

## Lead and opportunity workflows

When relevant, investigate or design:

- New inbound lead
- Under review
- Contact attempted
- Contacted
- Qualified opportunity
- Disqualified lead
- Closed won
- Closed lost
- Reopened

Do not force these states when source material defines a different funnel.

Explicitly address:

- Duplicate callers and repeat calls
- Transcript, summary, and extracted-answer storage
- Qualification evidence
- Disqualification reasons
- Sales outcomes
- Manual overrides
- Multiple businesses, teams, and agents
- Assignment changes
- Audit history
