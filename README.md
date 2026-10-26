# OpenCode agent and skill bundle

This repository defines focused AI coding agents and reusable skills. Its primary product is a clear, deterministic path from an approved request to a validated change.

## Core model

- **Agents** own a user-facing role, boundaries, delegation, and completion.
- **Skills** perform one reusable procedure with explicit inputs and minimum permissions.
- **`sdlc-orchestrator`** selects authority and an implementation specialist, then returns validation evidence.
- **`project-validation`** is required after code-editing work.

The default flow is:

1. Clarify a blocking ambiguity.
2. Establish missing authority.
3. Select one specialist.
4. Implement and validate.
5. Report changed paths and evidence.

## Optional GitHub adapter

GitHub issue and pull-request actions are available only when explicitly requested. They support issue creation, updates, comments, closure, and draft pull-request publication. They do not control the normal coding workflow and never automatically merge, delete branches, recover interrupted hosted state, or close issues.

## Layout

- `agents/` — user-facing roles and ordered workflows.
- `skills/` — focused procedures and any small supporting scripts.
- `tests/` — structural checks for identities, workflow edges, permissions, links, and YAML style.

Edit `/code` assets directly. Restart OpenCode after configuration changes so it reloads the active configuration.
