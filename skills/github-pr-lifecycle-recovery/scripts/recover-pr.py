#!/usr/bin/env python3
"""Recover a unique non-issue branch and pull-request lifecycle state."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def classify(
    prs: list[dict],
    remote_head: str | None,
    local_head: str,
    base_head: str,
    provenance: str,
    base: str = "main",
    clean: bool = True,
    expected_head: str | None = None,
) -> tuple[str, str | None, str | None]:
    if len(prs) > 1:
        return "blocked-unsafe", None, "multiple pull requests use the current branch"
    if not prs:
        if remote_head:
            if remote_head != local_head:
                return "blocked-unsafe", None, "local and remote branch heads differ without a pull request"
            return "remote-branch-no-pr", "pr-publication", None
        if local_head != base_head:
            if not clean:
                return "waiting-user-cleanup", None, "local worktree contains uncommitted changes"
            if expected_head == local_head:
                return "local-commit-no-remote", "pr-publication", None
            return "blocked-unsafe", None, "unpublished local commits lack durable remote ownership evidence"
        next_stage = "ownership-baseline" if provenance == "cli" else "worktree-validation"
        return "fresh-local", next_stage, None
    pr = prs[0]
    if any(not pr.get(key) for key in ("url", "headRefName", "headRefOid", "baseRefName")):
        return "blocked-unsafe", None, "current branch pull-request identity is incomplete"
    if pr.get("baseRefName") != base or f"OpenCode-Origin: {provenance}" not in (pr.get("body") or "").splitlines():
        return "blocked-unsafe", None, "current branch pull-request base or provenance is invalid"
    if pr.get("state") == "MERGED":
        if pr.get("headRefOid") != local_head:
            return "blocked-unsafe", None, "local and merged pull-request heads differ"
        if remote_head:
            if remote_head != pr.get("headRefOid"):
                return "blocked-unsafe", None, "remote branch no longer points to the merged head"
            return "merged-needs-cleanup", "remote-branch-cleanup", None
        return "merged", None, None
    if pr.get("state") != "OPEN":
        return "blocked-unsafe", None, "current branch has a non-open pull request"
    if pr.get("headRefOid") != local_head or remote_head != local_head:
        return "blocked-unsafe", None, "local, remote, and pull-request heads differ"
    return "open-pull-request", "hosted-checks", None


def emit(status: str, disposition: str, next_stage: str | None, evidence: dict, blocker: str | None = None) -> int:
    print(json.dumps({"version": 1, "status": status, "disposition": disposition, "next_stage": next_stage, "evidence": evidence, "blocker": blocker}, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provenance", choices=("cli", "openchamber"), required=True)
    parser.add_argument("--base", default="main")
    parser.add_argument("--expected-head")
    args = parser.parse_args()
    evidence: dict[str, object] = {}
    branch = run(["git", "branch", "--show-current"])
    head = run(["git", "rev-parse", "HEAD"])
    base_head_result = run(["git", "rev-parse", args.base])
    status_result = run(["git", "status", "--porcelain=v1"])
    if branch.returncode != 0 or head.returncode != 0 or base_head_result.returncode != 0 or status_result.returncode != 0 or not branch.stdout.strip() or branch.stdout.strip() == args.base:
        return emit("blocked", "blocked-unsafe", None, evidence, "current branch identity is invalid")
    branch_name = branch.stdout.strip()
    local_head = head.stdout.strip()
    base_head = base_head_result.stdout.strip()
    clean = status_result.stdout == ""
    evidence.update({"provenance": args.provenance, "branch": branch_name, "local_head": local_head, "base_head": base_head, "clean": clean, "expected_head": args.expected_head})
    if args.provenance == "cli" and not branch_name.startswith("feature/"):
        return emit("blocked", "blocked-unsafe", None, evidence, "cli recovery requires an orchestrator-owned feature/* branch")
    auth = run(["gh", "auth", "status"])
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    if auth.returncode != 0 or repo.returncode != 0:
        return emit("waiting", "waiting-external", None, evidence, (auth.stderr or repo.stderr).strip())
    try:
        repository = json.loads(repo.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", None, evidence, "invalid repository JSON")
    if not isinstance(repository, dict) or not repository.get("nameWithOwner") or not repository.get("url"):
        return emit("blocked", "blocked-unsafe", None, evidence, "repository identity is incomplete")
    evidence["repository"] = repository
    remote = run(["git", "ls-remote", "--heads", "origin", branch_name])
    listed = run(["gh", "pr", "list", "--head", branch_name, "--state", "all", "--json", "number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt"])
    if remote.returncode != 0 or listed.returncode != 0:
        return emit("waiting", "waiting-external", None, evidence, (remote.stderr or listed.stderr).strip())
    remote_head = remote.stdout.split()[0] if remote.stdout.strip() else None
    try:
        prs = json.loads(listed.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", None, evidence, "invalid pull-request list JSON")
    if not isinstance(prs, list) or any(not isinstance(record, dict) for record in prs):
        return emit("blocked", "blocked-unsafe", None, evidence, "pull-request list shape is invalid")
    disposition, next_stage, blocker = classify(prs, remote_head, local_head, base_head, args.provenance, args.base, clean, args.expected_head)
    evidence.update({"remote_head": remote_head, "pull_requests": prs})
    status = "waiting" if disposition == "waiting-user-cleanup" else "blocked" if disposition == "blocked-unsafe" else "passed"
    return emit(status, disposition, next_stage, evidence, blocker)


if __name__ == "__main__":
    sys.exit(main())
