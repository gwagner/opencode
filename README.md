# OpenCode agent and skill bundle

This repository defines focused AI coding agents and reusable skills. Its primary product is a clear, deterministic path from an approved request to a validated change.

## Core model

- **Agents** own a user-facing role, boundaries, delegation, and completion.
- **Skills** perform one reusable procedure with explicit inputs and minimum permissions.
- **`sdlc-orchestrator`** selects authority and an implementation specialist, then returns validation evidence.
- **`project-validation`** is required after code-editing work.

The OpenChamber-first default flow is:

1. Validate the selected OpenChamber-linked worktree without changing it. Prepare a fresh local branch only when the requester explicitly asks.
2. Clarify a blocking ambiguity.
3. Establish missing authority.
4. Select one specialist.
5. Implement and validate.
6. Report changed paths and evidence, leaving the result uncommitted unless the user separately authorizes a commit.

## Optional GitHub adapter

GitHub issue and pull-request actions are available only when explicitly requested. They support issue creation, updates, comments, closure, and draft pull-request publication. OpenCode's native approval gate prompts before a delegated commit or publication command runs. Publication reports `branch-pushed; pull-request-not-created` when a push succeeds but draft-PR creation fails; it does not retry or recover that partial state. These adapters do not control the normal coding workflow and never automatically merge, delete branches, recover interrupted hosted state, or close issues. The ordered-rule behavior and matcher tests follow the pinned OpenCode v2.1.2 [permission evaluator](https://github.com/anomalyco/opencode/blob/a517687fde98a7329ada3ae644a01a9fc6c4e99e/packages/core/src/permission.ts) and [wildcard implementation](https://github.com/anomalyco/opencode/blob/a517687fde98a7329ada3ae644a01a9fc6c4e99e/packages/core/src/util/wildcard.ts).

## Layout

- `agents/` — user-facing roles and ordered workflows.
- `skills/` — focused procedures and any small supporting scripts.
- `tests/` — structural and behavioral checks for identities, workflow edges, permissions, Git helpers, publication safety, links, and YAML style.

Edit `/code` assets directly. Restart OpenCode after configuration changes so it reloads the active configuration.

## Supported deployment

The checked-in stack pins **OpenCode 2.1.2** and **OpenChamber 2.5.3**. OpenCode 2.1.2 is the approved permission runtime: ordered permission rules use last-match-wins evaluation and the whole-resource wildcard behavior covered by `tests/test_pr_lifecycle_remediation.py`. Upgrade both the image pins and compatibility tests together; an unvalidated runtime is not supported.

### Configuration source and mounts

This deployment uses an **external OpenCode server** from OpenChamber's perspective: the `opencode` service owns the server process, while OpenChamber connects through `OPENCODE_HOST` with `OPENCODE_SKIP_START=true`. It is not OpenChamber-managed mode. In particular, OpenChamber's `openchamber` and `openchamber_schedule` agent tools are unavailable in external/skip-start mode; this bundle neither configures nor claims those tools. Worktree selection and specialist delegation use OpenCode's own runtime interfaces.

`openchamber.yaml` bind-mounts this repository at `/home/opencode/.config/opencode`, and the OpenCode image starts as `/home/opencode`. OpenCode's documented global discovery therefore loads:

- `opencode.jsonc` as its global configuration;
- `agents/` and `skills/` as the deployed definitions;
- `AGENTS.md` as global instructions;
- `/opt/plugins/` as the image-provided external skill directory.

The bundle owns the mounted global configuration and agent/skill definitions. `/opt/plugins/` is image-managed external content. Project, remote organizational, environment-selected, or system-managed OpenCode configuration can still merge with or override the global layer according to OpenCode precedence; inspect the resolved runtime configuration rather than assuming this checkout is the only source.

The repository does not reference a generated Graphify JavaScript plugin or invent a Graphify tool. Graphify is installed only as a CLI in the OpenCode image. OpenCode and OpenChamber share `/workspace`, `/worktrees`, and `/tmp/opencode`; the Obsidian vault is mounted at `/vault` for OpenCode.

| Variable | Required | Purpose |
| --- | --- | --- |
| `OPENCODE_SERVER_PASSWORD` | Yes | Shared authentication secret for OpenCode and OpenChamber. |
| `OPENCHAMBER_UI_PASSWORD` | Yes | Password protecting the OpenChamber web UI. |
| `HOME` | Yes | Resolves host SSH, GitHub CLI, and Git configuration mounts. |
| `CONTAINER_ENGINE` | No | Image builder used by `build.sh`; defaults to `docker`. |

Host directories and credential files named in `openchamber.yaml` must exist before startup. In particular, provision `/opt/opencode/{workspace,config,local,worktrees,tmp}`, `/opt/openchamber/config`, `/opt/obsidian/{vault,config}`, `${HOME}/.container-ssh/`, and `${HOME}/.config-gh/hosts.yml` with permissions appropriate for the container users.

### Build and start

Run from the repository root:

```sh
python3 scripts/validate-deployment.py
./tests/agent-skill-architecture.sh
./build.sh
docker compose -f openchamber.yaml config --quiet
docker compose -f openchamber.yaml up -d
```

Set `CONTAINER_ENGINE=podman` only when the same engine will run the resulting images and its Compose implementation supports this file. `build.sh` resolves Dockerfile paths relative to itself, so it may be invoked from another directory.

OpenChamber connects to `http://opencode:4096` with `OPENCODE_SKIP_START=true`; it must not launch a second, floating OpenCode runtime. In OpenChamber, select `sdlc-orchestrator` as the primary agent for coding work. A direct CLI selection of that same agent is an explicit fallback, not an intermediate launch step.

### Reload and smoke verification

Agent, skill, instruction, and `opencode.jsonc` changes require an OpenCode container restart. Dockerfile or version changes require rebuilding the affected image first.

```sh
docker compose -f openchamber.yaml restart opencode openchamber
docker exec opencode opencode --version
docker exec openchamber npm list -g @openchamber/web @opencode/cli
docker exec openchamber sh -c 'curl -fsS -u "opencode:$OPENCODE_SERVER_PASSWORD" http://opencode:4096/api/info'
```

The expected versions are OpenCode `2.1.2`, `@openchamber/web@2.5.3`, and `@opencode/cli@2.1.2`. The API response must report OpenCode 2.1.2. Also inspect the resolved OpenCode configuration with the deployed runtime's supported debug/config interface and confirm that `sdlc-orchestrator` and its specialist agents are discovered from the mounted global directory. Do not substitute an unverified command when that runtime exposes no such interface; record the startup/API evidence and treat capability validation as blocked.

Then open `http://localhost:3000`, select `sdlc-orchestrator`, and verify primary-agent launch, serial specialist delegation, native approval, and permission enforcement. Its first coding handoff must use the selected linked worktree without creating a branch, commit, pull request, or recovery action. Explicit branch preparation, commit, and publication must each produce a separate native approval path. Static checks do not establish these runtime capabilities; if any cannot be observed, the deployment is unsupported and execution must fail closed.

`docker compose ... config --quiet`, `scripts/validate-deployment.py`, and `tests/agent-skill-architecture.sh` are non-starting checks. The shell test is the standard repository test entry point and includes the Python behavioral suite. This repository does not automatically rebuild, restart, or reload a running stack.
