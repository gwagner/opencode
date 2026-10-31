#!/usr/bin/env python3
"""Capture an immutable, non-mutating Git ownership baseline."""
from __future__ import annotations

import json
import subprocess
import sys


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def parse_status(value: str) -> list[dict[str, str]]:
    """Parse `git status --porcelain=v1 -z` without losing rename paths."""
    fields = value.split("\0")
    entries: list[dict[str, str]] = []
    index = 0
    while index < len(fields) and fields[index]:
        field = fields[index]
        if len(field) < 4 or field[2] != " ":
            raise ValueError("unexpected porcelain status record")
        status = field[:2]
        entry = {"status": status, "path": field[3:]}
        index += 1
        if "R" in status or "C" in status:
            if index >= len(fields) or not fields[index]:
                raise ValueError("rename or copy record lacks its original path")
            entry["original_path"] = fields[index]
            index += 1
        entries.append(entry)
    return entries


def report(status: str, **evidence: object) -> int:
    print(json.dumps({"status": status, **evidence}, sort_keys=True))
    return 0 if status == "passed" else 2


def main() -> int:
    branch = run("git", "branch", "--show-current")
    head = run("git", "rev-parse", "--verify", "HEAD^{commit}")
    staged = run("git", "diff", "--cached", "--quiet", "--exit-code")
    status = run("git", "status", "--porcelain=v1", "-z", "--untracked-files=all")
    if branch.returncode or head.returncode or staged.returncode not in {0, 1} or status.returncode:
        return report("blocked", blocker="current Git state cannot be inspected")
    if not branch.stdout.strip():
        return report("blocked", blocker="baseline requires an attached branch")
    if staged.returncode == 1:
        return report(
            "blocked",
            branch=branch.stdout.strip(),
            baseline_commit=head.stdout.strip(),
            blocker="baseline requires an empty index",
        )
    try:
        changes = parse_status(status.stdout)
    except ValueError as error:
        return report("blocked", blocker=str(error))
    return report(
        "passed",
        branch=branch.stdout.strip(),
        baseline_commit=head.stdout.strip(),
        preexisting_changes=changes,
    )


if __name__ == "__main__":
    raise SystemExit(main())
