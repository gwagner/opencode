#!/usr/bin/env python3
"""Create one unused local feature branch from a clean base branch."""
import argparse
import json
import re
import subprocess
import sys


def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--outcome", required=True)
    parser.add_argument("--base", default="main")
    args = parser.parse_args()
    slug = re.sub(r"[^a-z0-9]+", "-", args.outcome.lower()).strip("-")[:48]
    branch = f"feature/{slug}"
    if not slug:
        print("outcome cannot produce a branch slug", file=sys.stderr)
        return 2
    if run("git", "status", "--porcelain=v1").stdout or run("git", "branch", "--show-current").stdout.strip() != args.base:
        print("worktree must be clean and attached to the base branch", file=sys.stderr)
        return 2
    if run("git", "branch", "--list", branch).stdout.strip():
        print(f"branch exists: {branch}", file=sys.stderr)
        return 2
    result = run("git", "switch", "-c", branch, args.base)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        return 1
    print(json.dumps({"branch": branch, "base": args.base}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
