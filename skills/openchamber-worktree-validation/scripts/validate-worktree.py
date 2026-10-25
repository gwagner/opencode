#!/usr/bin/env python3
"""Validate one existing linked worktree without destructive Git operations."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass


VERSION = 1


@dataclass
class Result:
    version: int = VERSION
    status: str = "blocked"
    disposition: str = "blocked-unsafe"
    next_stage: str | None = None
    evidence: dict | None = None
    blocker: str | None = None


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def classify(mode: str, clean: bool, head: str, base: str, expected_head: str | None) -> tuple[str, str | None]:
    if not clean:
        return "waiting-user-cleanup", "worktree contains unowned or uncommitted changes"
    if mode == "resume":
        if expected_head and head != expected_head:
            return "blocked-unsafe", "current head differs from the expected resumable head"
        if head != base:
            return "resume-publication", None
    if mode == "fresh" and head != base:
        return "blocked-unsafe", "fresh worktree contains commits not established as owned resume state"
    return "passed", None


def current_worktree_blocks(listing: str, root: str) -> list[list[str]]:
    """Return porcelain blocks that identify the exact current worktree."""
    blocks = []
    for raw_block in listing.split("\n\n"):
        lines = [line for line in raw_block.splitlines() if line]
        if f"worktree {root}" in lines:
            blocks.append(lines)
    return blocks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fresh", "resume"), required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--expected-head")
    args = parser.parse_args()

    evidence: dict[str, object] = {}
    inside = run("git", "rev-parse", "--is-inside-work-tree")
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        result = Result(evidence=evidence, blocker="current directory is not a Git worktree")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2

    commands = {
        "root": ("git", "rev-parse", "--show-toplevel"),
        "git_dir": ("git", "rev-parse", "--git-dir"),
        "common_dir": ("git", "rev-parse", "--git-common-dir"),
        "branch": ("git", "branch", "--show-current"),
        "head": ("git", "rev-parse", "HEAD"),
        "status": ("git", "status", "--porcelain=v1"),
        "worktrees": ("git", "worktree", "list", "--porcelain"),
    }
    values: dict[str, str] = {}
    for name, command in commands.items():
        completed = run(*command)
        if completed.returncode != 0:
            result = Result(evidence=evidence, blocker=f"failed to resolve {name}: {completed.stderr.strip()}")
            print(json.dumps(asdict(result), sort_keys=True))
            return 2
        values[name] = completed.stdout.strip()

    evidence.update(values)
    root = values["root"]
    branch = values["branch"]
    if values["git_dir"] == values["common_dir"]:
        result = Result(evidence=evidence, blocker="current checkout is not a linked worktree")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2
    if not branch or branch == args.base:
        result = Result(evidence=evidence, blocker="linked worktree must have an attached non-base branch")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2
    current_blocks = current_worktree_blocks(values["worktrees"], root)
    if len(current_blocks) != 1:
        result = Result(evidence=evidence, blocker="current worktree identity is missing or ambiguous")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2
    current_block = current_blocks[0]
    if any(line == "detached" or line.startswith("locked") or line.startswith("prunable") for line in current_block):
        result = Result(evidence=evidence, blocker="current worktree has unsafe topology metadata")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2

    fetched = run("git", "fetch", "origin", args.base)
    if fetched.returncode != 0:
        result = Result(status="waiting", disposition="waiting-external", evidence=evidence, blocker=fetched.stderr.strip())
        print(json.dumps(asdict(result), sort_keys=True))
        return 3
    remote = run("git", "rev-parse", f"origin/{args.base}")
    if remote.returncode != 0:
        result = Result(evidence=evidence, blocker="cannot resolve refreshed base revision")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2
    evidence["base_revision"] = remote.stdout.strip()

    disposition, blocker = classify(
        args.mode,
        values["status"] == "",
        values["head"],
        remote.stdout.strip(),
        args.expected_head,
    )
    status = "passed" if disposition in ("passed", "resume-publication") else "waiting" if disposition == "waiting-user-cleanup" else "blocked"
    next_stage = "ownership-baseline" if disposition == "passed" else "pr-publication" if disposition == "resume-publication" else None
    result = Result(status=status, disposition=disposition, next_stage=next_stage, evidence=evidence, blocker=blocker)
    print(json.dumps(asdict(result), sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


if __name__ == "__main__":
    sys.exit(main())
