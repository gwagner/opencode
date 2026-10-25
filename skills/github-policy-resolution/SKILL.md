---
name: github-policy-resolution
description: Resolves one read-only lifecycle policy source into the fixed immutable snapshot used by one SDLC run.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/github-policy-resolution/scripts/resolve-policy.py *": allow
  read:
    "/tmp/opencode/lifecycle-policy.json": allow
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
  edit:
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/code/skills/github-policy-resolution/scripts/resolve-policy.py": allow
inputs:
  - optional read-only `/tmp/opencode/lifecycle-policy.json`
  - retained snapshot digest when resuming or cleaning up
  - verified terminal disposition when cleaning up
---

# GitHub lifecycle policy resolution

## Inputs

Require the optional read-only `/tmp/opencode/lifecycle-policy.json`. The only output path is `/tmp/opencode/lifecycle-policy.snapshot.json`; callers cannot select either path.

## Procedure

1. Run `python3 /code/skills/github-policy-resolution/scripts/resolve-policy.py` as the lifecycle's first stage. If the snapshot is absent, it validates and normalizes the optional source or the default policy, creates the fixed snapshot once, and emits its digest.
2. On resumption, run the same command with `--expected-policy-digest <digest>` retained from lifecycle evidence. It validates only the fixed snapshot bytes; it does not reread the source.
3. Pass the emitted snapshot and digest as `--policy /tmp/opencode/lifecycle-policy.snapshot.json --expected-policy-digest <digest>` to every lifecycle consumer. Never pass the source path again.
4. Clean up only after a verified terminal lifecycle report: run `python3 /code/skills/github-policy-resolution/scripts/resolve-policy.py --cleanup --terminal-disposition <user-merged|closed|rejected-open-pr> --expected-policy-digest <digest>`. This removes only the exact fixed snapshot after re-verifying its digest.

## Completion

Report the fixed snapshot path and digest. A malformed source, missing resumption digest, non-normalized snapshot, or digest mismatch is `blocked`.
