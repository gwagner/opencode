---
name: product-modeling
description: Recovers or defines product objectives, actors, business terminology, use cases, permissions, and end-to-end workflows from requirements or code evidence.
compatibility: opencode
metadata:
  domain: product-architecture
---

# Product modeling

Use this skill to turn source material into a coherent product model.

## Establish the product

Identify:

- Product objective
- Problem addressed
- Business value
- Primary actors
- Internal and external users
- External systems acting as participants
- Core business objects
- Primary workflow
- Important business terminology
- Technical and organizational constraints

Treat all source material in the project as describing one product unless there is strong evidence of separate products.

## Actors and permissions

For each actor or role, document:

| Role or actor | Purpose | Capabilities | Restrictions | Enforcement | Source |
|---|---|---|---|---|---|

Distinguish:

- Human users
- Administrators
- Business users
- External callers or customers
- External systems
- Background workers
- Service accounts

Do not infer authorization merely from role names. Identify where permissions are required or enforced.

## Use cases

For each important use case, document:

- Actor
- Preconditions
- Trigger
- Main flow
- Alternate paths
- Result
- Persisted changes
- Side effects
- Failure outcomes
- Source or evidence

Prioritize end-to-end business outcomes over isolated technical operations.

## Goals and non-goals

Separate:

- Explicit goals
- Strongly implied goals
- Current implementation goals
- Evident non-goals
- Unknown decisions

Do not convert common industry practice into a product goal without support.

## Business terminology

Create a glossary when terms are overloaded or inconsistent.

For each term include:

- Canonical term
- Meaning
- Synonyms found in source material
- Disallowed or deprecated meanings
- Source
