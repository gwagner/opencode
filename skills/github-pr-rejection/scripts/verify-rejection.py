#!/usr/bin/env python3
"""Verify the non-mutating terminal result of an exact-head PR rejection."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def matches(record: dict, head: str, base: str) -> bool:
    return record.get("state") == "OPEN" and record.get("headRefOid") == head and record.get("baseRefName") == base and bool(record.get("headRefName"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-base", default="main")
    args = parser.parse_args()
    evidence: dict[str, object] = {}
    auth = run(["gh", "auth", "status"])
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    viewed = run(["gh", "pr", "view", args.pr, "--json", "number,url,state,baseRefName,headRefName,headRefOid"])
    if auth.returncode != 0 or repo.returncode != 0 or viewed.returncode != 0:
        print(json.dumps({"version": 1, "status": "waiting", "disposition": "waiting-external", "next_stage": "user-decision", "evidence": evidence, "blocker": (auth.stderr or repo.stderr or viewed.stderr).strip()}, sort_keys=True))
        return 3
    try:
        evidence["repository"] = json.loads(repo.stdout)
        evidence["pull_request"] = json.loads(viewed.stdout)
    except json.JSONDecodeError:
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": None, "evidence": evidence, "blocker": "invalid GitHub JSON"}, sort_keys=True))
        return 2
    if not matches(evidence["pull_request"], args.expected_head, args.expected_base):
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": "user-decision", "evidence": evidence, "blocker": "pull request changed after rejection"}, sort_keys=True))
        return 2
    print(json.dumps({"version": 1, "status": "passed", "disposition": "rejected-open-pr", "next_stage": None, "evidence": evidence, "blocker": None}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
