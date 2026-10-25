#!/usr/bin/env python3
"""Verify the non-mutating terminal result of an exact-head PR rejection."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_authorization_argument, add_policy_argument, authorized, load_policy, policy_evidence
from github_pr_lifecycle_common import emit, head_repository_matches, parse_object, remote_urls_match, repository_matches, run, verified_checkout

def matches(record: dict, head: str, base: str, branch: str) -> bool:
    return record.get("state") == "OPEN" and record.get("headRefOid") == head and record.get("baseRefName") == base and record.get("headRefName") == branch

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--expected-base", default=None)
    add_policy_argument(parser)
    add_authorization_argument(parser, "rejection")
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy)
    except ValueError as exc:
        return emit("blocked", "blocked-unsafe", {}, str(exc))
    if args.expected_base is None:
        args.expected_base = policy["base_branch"]
    evidence: dict[str, object] = policy_evidence(policy)
    state, repository, blocker = verified_checkout(run, evidence)
    if state != "passed":
        return emit(state, "waiting-external" if state == "waiting" else "blocked-unsafe", evidence, blocker, "user-decision" if state == "waiting" else None)
    origin = run(["git", "remote", "get-url", "--all", policy["remote"]])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", policy["remote"]])
    if origin.returncode != 0 or push_origin.returncode != 0 or not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return emit("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository")
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    viewed = run(["gh", "pr", "view", args.pr, "--repo", repository["nameWithOwner"], "--json", "number,url,state,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"])
    if viewed.returncode != 0:
        return emit("waiting", "waiting-external", evidence, viewed.stderr.strip(), "user-decision")
    pull_request = parse_object(viewed)
    if pull_request is None:
        return emit("blocked", "blocked-unsafe", evidence, "invalid pull-request JSON")
    evidence["pull_request"] = pull_request
    if not repository_matches(repository, pull_request) or not head_repository_matches(repository, pull_request):
        return emit("blocked", "blocked-unsafe", evidence, "pull request does not belong to the current repository", "user-decision")
    if not matches(pull_request, args.expected_head, args.expected_base, args.expected_branch):
        return emit("blocked", "blocked-unsafe", evidence, "pull request changed after rejection", "user-decision")
    if policy["pull_request"]["rejection_policy"] == "close-pr":
        if not authorized(policy, "rejection", args.authorize_rejection):
            return emit("waiting", "waiting-user-authorization", evidence, "explicit rejection-close authorization is required")
        closed = run(["gh", "pr", "close", str(pull_request["number"]), "--repo", repository["nameWithOwner"]])
        verified = run(["gh", "pr", "view", str(pull_request["number"]), "--repo", repository["nameWithOwner"], "--json", "state,headRefOid,headRefName,baseRefName"])
        closed_record = parse_object(verified)
        if closed.returncode != 0 or not closed_record or closed_record.get("state") != "CLOSED" or closed_record.get("headRefOid") != args.expected_head or closed_record.get("headRefName") != args.expected_branch or closed_record.get("baseRefName") != args.expected_base:
            return emit("waiting", "waiting-external", evidence, closed.stderr.strip() or "rejection close was not verified")
        evidence["rejection_close"] = "verified"
        return emit("passed", "rejected-closed-pr", evidence)
    return emit("passed", "rejected-open-pr", evidence)

if __name__ == "__main__":
    sys.exit(main())
