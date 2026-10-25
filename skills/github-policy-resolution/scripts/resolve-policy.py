#!/usr/bin/env python3
"""Resolve a caller policy once into a fixed, immutable lifecycle snapshot."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import SNAPSHOT_PATH, load_policy, resolve_policy_source

SOURCE = Path("/tmp/opencode/lifecycle-policy.json")
SNAPSHOT = Path(SNAPSHOT_PATH)
TERMINAL_DISPOSITIONS = ("user-merged", "closed", "rejected-open-pr")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-policy-digest")
    parser.add_argument("--cleanup", action="store_true")
    parser.add_argument("--terminal-disposition", choices=TERMINAL_DISPOSITIONS)
    args = parser.parse_args()
    try:
        if args.cleanup:
            if args.terminal_disposition is None or args.expected_policy_digest is None:
                raise ValueError("cleanup requires an exact terminal disposition and expected policy digest")
            load_policy(str(SNAPSHOT), args.expected_policy_digest)
            SNAPSHOT.unlink()
            print(json.dumps({"version": 1, "snapshot": str(SNAPSHOT), "digest": args.expected_policy_digest, "cleanup": "completed", "terminal_disposition": args.terminal_disposition}, sort_keys=True))
            return 0
        if args.terminal_disposition is not None:
            raise ValueError("terminal disposition is valid only with cleanup")
        if SNAPSHOT.exists():
            if args.expected_policy_digest is None:
                raise ValueError("resuming a lifecycle requires the exact policy snapshot digest")
            policy = load_policy(str(SNAPSHOT), args.expected_policy_digest)
            digest = policy["_snapshot_digest"]
        else:
            source = SOURCE.read_bytes() if SOURCE.exists() else None
            _, normalized, digest = resolve_policy_source(source)
            fd = os.open(SNAPSHOT, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o400)
            with os.fdopen(fd, "wb") as output:
                output.write(normalized)
            os.chmod(SNAPSHOT, 0o400)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"policy resolution failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({"version": 1, "snapshot": str(SNAPSHOT), "digest": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
