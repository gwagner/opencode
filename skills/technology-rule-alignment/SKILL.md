---
name: technology-rule-alignment
description: Routes one sourced technology or stack rule to the smallest existing agent or skill surface and defines future audit criteria.
classification: technical
opencode_permission:
  read: allow
inputs:
  - one technology or technology-stack rule with its source
  - caller-permitted candidate agent and skill Markdown paths
  - approved audit or revision scope
---

# Technology rule alignment

## Purpose

Route one sourced technology or technology-stack rule to its smallest owning agent or skill surface and define its future audit criterion.

## Inputs

Require one technology or technology-stack rule with its source, caller-permitted candidate agent and skill Markdown paths, and approved audit or revision scope.

## Boundaries

MUST read only caller-permitted candidates. MUST NOT modify files, invent a technology rule, infer unsupported applicability, create an agent, or perform an unapproved fleet-wide audit.

## Procedure

1. Verify the rule's source, scope, technology applicability, and approved candidates. Report missing source or ambiguous applicability.
2. Identify the smallest existing skill whose cohesive procedure owns the rule. If no skill owns it, identify the existing agent whose workflow owns it.
3. Prefer revising or creating a skill over creating an agent. Recommend a new agent only when no existing agent can expose the rule through its workflow and a distinct user-facing role is required.
4. Define an audit criterion using the rule source, applicable technology signal, owning definition, and required alignment evidence.
5. For future relevant audits or revisions, evaluate only candidates in the approved scope against that criterion. Do not trigger an immediate fleet-wide audit.
6. Report the owner, retained architecture, audit criterion, required revision, excluded candidates, and blockers.
