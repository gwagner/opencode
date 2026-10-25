#!/usr/bin/env python3
"""Validate one existing linked worktree without destructive Git operations."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_policy_argument, load_policy, policy_evidence


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


def classify(
    mode: str,
    clean: bool,
    head: str,
    base: str,
    expected_head: str | None,
    *,
    conflicts: bool = False,
    base_is_ancestor: bool | None = None,
    feature_commit_count: int | None = None,
) -> tuple[str, str | None]:
    if conflicts:
        return "blocked-unsafe", "worktree contains unresolved merge conflicts"
    if not clean:
        return "waiting-user-cleanup", "worktree contains unowned or uncommitted changes"
    if mode in ("resume-publication", "resume-pull-request"):
        if not expected_head:
            return "blocked-unsafe", "resumed worktree requires an expected task head"
        if head != expected_head:
            return "blocked-unsafe", "current head differs from the expected resumable head"
        if head == base:
            return "blocked-unsafe", "resumed worktree head does not differ from the base revision"
        if mode == "resume-publication":
            return "resume-publication", None
        return "resume-pull-request", None
    if mode == "fresh" and head != base:
        if base_is_ancestor is True and feature_commit_count == 0:
            return "passed", None
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
    parser.add_argument("--mode", choices=("fresh", "resume-publication", "resume-pull-request"), required=True)
    parser.add_argument("--base")
    parser.add_argument("--expected-head")
    add_policy_argument(parser)
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy, args.expected_policy_digest, args.repository, args.lifecycle_run)
    except ValueError as exc:
        print(json.dumps(asdict(Result(evidence={}, blocker=str(exc))), sort_keys=True))
        return 2
    if args.base is None:
        args.base = policy["base_branch"]
    if args.base != policy["base_branch"]:
        print(json.dumps(asdict(Result(evidence=policy_evidence(policy), blocker="base differs from lifecycle policy")), sort_keys=True))
        return 2

    evidence: dict[str, object] = policy_evidence(policy)
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
        "conflicts": ("git", "diff", "--name-only", "--diff-filter=U"),
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

    fetched = run("git", "fetch", policy["remote"], args.base)
    if fetched.returncode != 0:
        result = Result(status="waiting", disposition="waiting-external", evidence=evidence, blocker=fetched.stderr.strip())
        print(json.dumps(asdict(result), sort_keys=True))
        return 3
    remote = run("git", "rev-parse", f"{policy['remote']}/{args.base}")
    if remote.returncode != 0:
        result = Result(evidence=evidence, blocker="cannot resolve refreshed base revision")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2
    evidence["base_revision"] = remote.stdout.strip()
    ancestry = run("git", "merge-base", "--is-ancestor", values["head"], f"{policy['remote']}/{args.base}")
    if ancestry.returncode not in (0, 1):
        result = Result(evidence=evidence, blocker="cannot establish refreshed-base ancestry")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2
    feature_range = run("git", "rev-list", "--count", f"{policy['remote']}/{args.base}..{values['head']}")
    try:
        feature_commit_count = int(feature_range.stdout.strip()) if feature_range.returncode == 0 else -1
    except ValueError:
        feature_commit_count = -1
    if feature_commit_count < 0:
        result = Result(evidence=evidence, blocker="cannot establish refreshed-base feature range")
        print(json.dumps(asdict(result), sort_keys=True))
        return 2
    evidence["head_is_ancestor_of_refreshed_base"] = ancestry.returncode == 0
    evidence["feature_commit_count"] = feature_commit_count

    disposition, blocker = classify(
        args.mode,
        values["status"] == "",
        values["head"],
        remote.stdout.strip(),
        args.expected_head,
        conflicts=bool(values["conflicts"]),
        base_is_ancestor=ancestry.returncode == 0,
        feature_commit_count=feature_commit_count,
    )
    status = "passed" if disposition in ("passed", "resume-publication", "resume-pull-request") else "waiting" if disposition == "waiting-user-cleanup" else "blocked"
    next_stage = "pr-publication" if disposition == "resume-publication" else "ownership-baseline" if disposition in ("passed", "resume-pull-request") else None
    result = Result(status=status, disposition=disposition, next_stage=next_stage, evidence=evidence, blocker=blocker)
    print(json.dumps(asdict(result), sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


if __name__ == "__main__":
    sys.exit(main())
