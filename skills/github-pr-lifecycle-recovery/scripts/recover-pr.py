#!/usr/bin/env python3
"""Recover a unique non-issue branch and pull-request lifecycle state."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_policy_argument, load_policy, policy_evidence
from github_pr_lifecycle_common import (
    emit as result_emit,
    head_repository_matches,
    marker_matches,
    parse_remote_head,
    remote_urls_match,
    repository_matches,
    run,
)


def classify(
    prs: list[dict],
    remote_head: str | None,
    local_head: str,
    base_head: str,
    provenance: str,
    base: str = "main",
    clean: bool = True,
    expected_head: str | None = None,
    base_policy: str = "main",
) -> tuple[str, str | None, str | None]:
    if base != base_policy:
        return "blocked-unsafe", None, "non-issue lifecycle recovery base differs from policy"
    if len(prs) > 1:
        return "blocked-unsafe", None, "multiple pull requests use the current branch"
    if not prs:
        if not clean:
            return "waiting-user-cleanup", None, "local worktree contains uncommitted changes"
        if remote_head:
            if remote_head != local_head:
                return "blocked-unsafe", None, "local and remote branch heads differ without a pull request"
            if expected_head != local_head:
                return "blocked-unsafe", None, "remote branch without a pull request lacks retained validated-head evidence"
            next_stage = "pr-publication" if provenance == "cli" else "worktree-validation"
            return "remote-branch-no-pr", next_stage, None
        if local_head != base_head:
            if expected_head == local_head:
                next_stage = "pr-publication" if provenance == "cli" else "worktree-validation"
                return "local-commit-no-remote", next_stage, None
            return "blocked-unsafe", None, "unpublished local commits lack durable remote ownership evidence"
        next_stage = "ownership-baseline" if provenance == "cli" else "worktree-validation"
        return "fresh-local", next_stage, None
    pr = prs[0]
    if any(not pr.get(key) for key in ("url", "headRefName", "headRefOid", "baseRefName")):
        return "blocked-unsafe", None, "current branch pull-request identity is incomplete"
    if pr.get("baseRefName") != base or not marker_matches(pr, provenance):
        return "blocked-unsafe", None, "current branch pull-request base or provenance is invalid"
    if pr.get("state") == "MERGED":
        return "recovered-merged-needs-reattest", "user-merge-reattest", None
    if pr.get("state") != "OPEN":
        return "blocked-unsafe", None, "current branch has a non-open pull request"
    if pr.get("headRefOid") != local_head or remote_head != local_head:
        return "blocked-unsafe", None, "local, remote, and pull-request heads differ"
    if not clean:
        return "waiting-user-cleanup", None, "local worktree contains uncommitted changes"
    next_stage = "ownership-baseline" if provenance == "cli" else "worktree-validation"
    return "open-pull-request", next_stage, None



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provenance", choices=("cli", "openchamber"), required=True)
    parser.add_argument("--base", default=None)
    parser.add_argument("--expected-head")
    parser.add_argument("--pr", help="exact pull-request URL or number for recovery")
    add_policy_argument(parser)
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy)
    except ValueError as exc:
        return result_emit("blocked", "blocked-unsafe", {}, str(exc))
    if args.base is None:
        args.base = policy["base_branch"]
    evidence: dict[str, object] = policy_evidence(policy)
    if args.provenance not in policy["provenance"]:
        return result_emit("blocked", "blocked-unsafe", evidence, "provenance is not permitted by policy")
    if args.base != policy["base_branch"]:
        return result_emit("blocked", "blocked-unsafe", evidence, "non-issue lifecycle recovery base differs from policy", None)
    branch = run(["git", "branch", "--show-current"])
    head = run(["git", "rev-parse", "HEAD"])
    base_head_result = run(["git", "rev-parse", args.base])
    status_result = run(["git", "status", "--porcelain=v1"])
    if branch.returncode != 0 or head.returncode != 0 or base_head_result.returncode != 0 or status_result.returncode != 0 or not branch.stdout.strip() or branch.stdout.strip() == args.base:
        return result_emit("blocked", "blocked-unsafe", evidence, "current branch identity is invalid", None)
    branch_name = branch.stdout.strip()
    local_head = head.stdout.strip()
    base_head = base_head_result.stdout.strip()
    clean = status_result.stdout == ""
    evidence.update({"provenance": args.provenance, "branch": branch_name, "local_head": local_head, "base_head": base_head, "clean": clean, "expected_head": args.expected_head})
    if args.provenance == "cli" and not branch_name.startswith(policy["feature_branch_prefix"]):
        return result_emit("blocked", "blocked-unsafe", evidence, "cli recovery branch lacks the policy feature prefix", None)
    auth = run(["gh", "auth", "status"])
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    if auth.returncode != 0 or repo.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, (auth.stderr or repo.stderr).strip())
    try:
        repository = json.loads(repo.stdout)
    except json.JSONDecodeError:
        return result_emit("blocked", "blocked-unsafe", evidence, "invalid repository JSON", None)
    if not isinstance(repository, dict) or not repository.get("nameWithOwner") or not repository.get("url"):
        return result_emit("blocked", "blocked-unsafe", evidence, "repository identity is incomplete", None)
    evidence["repository"] = repository
    origin = run(["git", "remote", "get-url", "--all", policy["remote"]])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", policy["remote"]])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return result_emit("blocked", "blocked-unsafe", evidence, "origin remote identity is unavailable", None)
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return result_emit("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository", None)
    fields = "number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt,mergeCommit,isCrossRepository,headRepository"
    listed = run(["gh", "pr", "view", args.pr, "--repo", repository["nameWithOwner"], "--json", fields]) if args.pr else run(["gh", "pr", "list", "--repo", repository["nameWithOwner"], "--head", branch_name, "--state", "all", "--json", fields])
    if listed.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, listed.stderr.strip())
    try:
        decoded = json.loads(listed.stdout)
        prs = [decoded] if args.pr else decoded
    except json.JSONDecodeError:
        return result_emit("blocked", "blocked-unsafe", evidence, "invalid pull-request list JSON", None)
    if not isinstance(prs, list) or any(not isinstance(record, dict) for record in prs):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request list shape is invalid", None)
    if any(not (repository_matches(repository, record) and head_repository_matches(repository, record)) for record in prs):
        evidence["pull_requests"] = prs
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request repository identity is invalid", None)
    remote = run(["git", "ls-remote", "--heads", policy["remote"], branch_name])
    if remote.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, remote.stderr.strip())
    remote_head, remote_valid = parse_remote_head(remote.stdout, branch_name)
    if not remote_valid:
        return result_emit("blocked", "blocked-unsafe", evidence, "remote branch identity is ambiguous", None)
    disposition, next_stage, blocker = classify(prs, remote_head, local_head, base_head, args.provenance, args.base, clean, args.expected_head, policy["base_branch"])
    evidence.update({"remote_head": remote_head, "pull_requests": prs})
    status = "waiting" if disposition == "waiting-user-cleanup" else "blocked" if disposition == "blocked-unsafe" else "passed"
    return result_emit(status, disposition, evidence, blocker, next_stage)


if __name__ == "__main__":
    sys.exit(main())
