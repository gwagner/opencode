#!/usr/bin/env python3
"""Resolve a caller policy once into a fixed, immutable lifecycle snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import load_policy, resolve_policy_source, snapshot_path

SOURCE = Path("/tmp/opencode/lifecycle-policy.json")
TERMINAL_DISPOSITIONS = ("user-merged", "closed", "rejected-open-pr")


def terminal_evidence_path(lifecycle_run: str) -> Path:
    return Path("/tmp/opencode") / f"lifecycle-terminal.{lifecycle_run}.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-policy-digest")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--lifecycle-run", required=True)
    parser.add_argument("--terminal-evidence-digest")
    parser.add_argument("--terminal-evidence")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--terminal-disposition", choices=TERMINAL_DISPOSITIONS)
    args = parser.parse_args()
    try:
        snapshot = Path(snapshot_path(args.repository, args.lifecycle_run))
        if args.cleanup:
            if args.terminal_disposition is None or args.expected_policy_digest is None:
                raise ValueError("cleanup requires an exact terminal disposition and expected policy digest")
            # Cleanup is evidence-bound: terminal state must be supplied by the
            # caller's verified terminal envelope, never merely a disposition.
            if not args.terminal_evidence_digest or not args.terminal_evidence:
                raise ValueError("cleanup requires the exact terminal evidence digest")
            terminal_path = Path(args.terminal_evidence)
            if terminal_path != terminal_evidence_path(args.lifecycle_run):
                raise ValueError("terminal evidence path must be the lifecycle-run-bound /tmp/opencode result")
            terminal_bytes = terminal_path.read_bytes()
            if hashlib.sha256(terminal_bytes).hexdigest() != args.terminal_evidence_digest:
                raise ValueError("terminal evidence digest does not match its exact bytes")
            terminal = json.loads(terminal_bytes)
            if not isinstance(terminal, dict) or set(terminal) != {"version", "status", "disposition", "next_stage", "evidence", "blocker"} or terminal.get("version") != 1 or terminal.get("status") != "passed" or terminal.get("disposition") != args.terminal_disposition or terminal.get("next_stage") is not None or terminal.get("blocker") is not None:
                raise ValueError("terminal evidence does not prove the requested disposition")
            evidence = terminal.get("evidence")
            if not isinstance(evidence, dict) or evidence.get("policy_digest") != args.expected_policy_digest or evidence.get("policy_binding") != {"repository": args.repository, "lifecycle_run": args.lifecycle_run}:
                raise ValueError("terminal evidence is not bound to this policy snapshot")
            pull_request = evidence.get("pull_request")
            if not isinstance(pull_request, dict) or not all(pull_request.get(field) for field in ("url", "headRefName", "headRefOid", "baseRefName")):
                raise ValueError("terminal evidence lacks an immutable pull-request identity")
            load_policy(str(snapshot), args.expected_policy_digest, args.repository, args.lifecycle_run)
            snapshot.unlink()
            print(json.dumps({"version": 1, "snapshot": str(snapshot), "digest": args.expected_policy_digest, "repository": args.repository, "lifecycle_run": args.lifecycle_run, "cleanup": "completed", "terminal_disposition": args.terminal_disposition, "terminal_evidence_digest": args.terminal_evidence_digest}, sort_keys=True))
            return 0
        if args.terminal_disposition is not None:
            raise ValueError("terminal disposition is valid only with cleanup")
        if snapshot.exists():
            if args.expected_policy_digest is None:
                raise ValueError("resuming a lifecycle requires the exact policy snapshot digest")
            policy = load_policy(str(snapshot), args.expected_policy_digest, args.repository, args.lifecycle_run)
            digest = policy["_snapshot_digest"]
        else:
            source = SOURCE.read_bytes() if SOURCE.exists() else None
            _, normalized, digest = resolve_policy_source(source, args.repository, args.lifecycle_run)
            fd = os.open(snapshot, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o400)
            with os.fdopen(fd, "wb") as output:
                output.write(normalized)
            os.chmod(snapshot, 0o400)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"policy resolution failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"version": 1, "snapshot": str(snapshot), "digest": digest, "repository": args.repository, "lifecycle_run": args.lifecycle_run}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
