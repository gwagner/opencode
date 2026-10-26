#!/usr/bin/env python3
"""Post one caller-provided GitHub issue comment."""
import argparse
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    args = parser.parse_args()
    body = Path("/tmp/opencode/github-issue-manager-comment.md")
    if not body.is_file() or not body.read_text().strip():
        print("comment body is missing or empty", file=sys.stderr)
        return 2
    result = subprocess.run(["gh", "issue", "comment", args.issue, "--body-file", str(body)], text=True, capture_output=True, check=False)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
