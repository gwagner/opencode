#!/usr/bin/env python3
"""Push the current branch and create one draft pull request."""
import argparse
import subprocess
import sys
from pathlib import Path


def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True, type=Path)
    parser.add_argument("--base", default="main")
    args = parser.parse_args()
    try:
        with args.body_file.open("rb"):
            pass
    except OSError as error:
        print(f"pull-request body file is not readable: {error}", file=sys.stderr)
        return 2
    branch = run("git", "branch", "--show-current")
    status = run("git", "status", "--porcelain=v1")
    if branch.returncode or status.returncode or not branch.stdout.strip() or branch.stdout.strip() == args.base or status.stdout:
        print("publication requires a clean committed non-base branch", file=sys.stderr)
        return 2
    pushed = run("git", "push", "--set-upstream", "origin", branch.stdout.strip())
    if pushed.returncode:
        print(pushed.stderr, file=sys.stderr)
        return pushed.returncode
    created = run("gh", "pr", "create", "--draft", "--base", args.base, "--head", branch.stdout.strip(), "--title", args.title, "--body-file", str(args.body_file))
    if created.returncode:
        print(created.stderr, file=sys.stderr)
        return created.returncode
    print(created.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
