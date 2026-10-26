#!/usr/bin/env python3
"""Close one user-selected GitHub issue."""
import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    args = parser.parse_args()
    result = subprocess.run(["gh", "issue", "close", args.issue], text=True, capture_output=True, check=False)
    if result.returncode:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    print(result.stdout.strip())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
