---
name: github-policy-resolution
description: Resolves one read-only lifecycle policy source into the repository-and-run-bound immutable snapshot used by one SDLC run.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-policy-resolution/scripts/resolve-policy.py *": allow
  read:
    "/tmp/opencode/lifecycle-policy.json": allow
    "/tmp/opencode/lifecycle-policy.*.snapshot.json": allow
  edit:
    "/tmp/opencode/lifecycle-policy.*.snapshot.json": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/code/skills/github-policy-resolution/scripts/resolve-policy.py": allow
inputs:
  - optional read-only `/tmp/opencode/lifecycle-policy.json`
  - exact repository owner/name and immutable lifecycle run ID
  - retained snapshot digest when resuming or cleaning up
  - immutable terminal result envelope and SHA-256 digest when cleaning up
---

# GitHub lifecycle policy resolution

## Inputs

Require the optional read-only `/tmp/opencode/lifecycle-policy.json`, exact repository owner/name, and opaque immutable lifecycle run ID. The only output path is `/tmp/opencode/lifecycle-policy.<repository-hash>.<lifecycle-run>.snapshot.json`; callers cannot select the derived path.

## Procedure

1. Run `python3 /code/skills/github-policy-resolution/scripts/resolve-policy.py --repository <owner/name> --lifecycle-run <run-id>` as the lifecycle's first stage. If the bound snapshot is absent, it validates and normalizes the optional source or the default policy, creates it once with exclusive creation, and emits its digest.
2. On resumption, run the same command with `--expected-policy-digest <digest> --repository <owner/name> --lifecycle-run <run-id>` retained from lifecycle evidence. It validates only the bound snapshot bytes; it does not reread the source.
3. Pass the emitted snapshot and digest as `--policy /tmp/opencode/lifecycle-policy.<repository-hash>.<lifecycle-run>.snapshot.json --expected-policy-digest <digest> --repository <owner/name> --lifecycle-run <run-id>` to every lifecycle consumer. Never pass the source path again.
4. Clean up only after a verified terminal lifecycle report: run `python3 /code/skills/github-policy-resolution/scripts/resolve-policy.py --cleanup --terminal-disposition <user-merged|closed|rejected-open-pr> --terminal-evidence <envelope> --terminal-evidence-digest <sha256> --expected-policy-digest <digest> --repository <owner/name> --lifecycle-run <run-id>`. This removes only the exact bound snapshot after re-verifying its digest and the envelope's matching policy binding.

## Completion

Report the bound snapshot path and digest. A malformed source, missing resumption digest, non-normalized snapshot, digest mismatch, or mismatched terminal envelope is `blocked`.
