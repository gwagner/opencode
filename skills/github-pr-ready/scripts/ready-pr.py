#!/usr/bin/env python3
"""Idempotently mark one exact open pull request ready for review."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_authorization_argument, add_policy_argument, authorized, load_policy, policy_evidence
from github_pr_lifecycle_common import (
    emit as result_emit,
    head_repository_matches,
    parse_object,
    remote_urls_match,
    repository_matches,
    run,
)
FIELDS = "number,url,state,isDraft,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"




def identity_matches(record: dict, expected_head: str, expected_base: str, expected_branch: str) -> bool:
    return (
        record.get("state") == "OPEN"
        and record.get("headRefOid") == expected_head
        and record.get("baseRefName") == expected_base
        and record.get("headRefName") == expected_branch
        and bool(record.get("number"))
        and bool(record.get("url"))
        and bool(record.get("headRefName"))
        and isinstance(record.get("isDraft"), bool)
    )



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--expected-base", default=None)
    add_policy_argument(parser)
    add_authorization_argument(parser, "ready")
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy, args.expected_policy_digest)
    except ValueError as exc:
        return result_emit("blocked", "blocked-unsafe", {}, str(exc))
    if args.expected_base is None:
        args.expected_base = policy["base_branch"]
    if args.expected_base != policy["base_branch"]:
        return result_emit("blocked", "blocked-unsafe", policy_evidence(policy), "ready base must equal the lifecycle policy base")
    evidence: dict[str, object] = policy_evidence(policy)
    if not args.expected_branch.startswith(policy["feature_branch_prefix"]):
        return result_emit("blocked", "blocked-unsafe", evidence, "ready branch must use the lifecycle feature prefix")
    auth = run(["gh", "auth", "status"])
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    if auth.returncode != 0 or repo.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, (auth.stderr or repo.stderr).strip())
    repository = parse_object(repo)
    if not repository or not repository.get("nameWithOwner") or not repository.get("url"):
        return result_emit("blocked", "blocked-unsafe", evidence, "repository identity is malformed or incomplete")
    evidence["repository"] = repository

    origin = run(["git", "remote", "get-url", "--all", policy["remote"]])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", policy["remote"]])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return result_emit("blocked", "blocked-unsafe", evidence, "origin remote identity is unavailable")
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return result_emit("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository")

    before_result = run(["gh", "pr", "view", args.pr, "--repo", repository["nameWithOwner"], "--json", FIELDS])
    if before_result.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, before_result.stderr.strip())
    before = parse_object(before_result)
    if before is None:
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request JSON is malformed")
    evidence["before"] = before
    if not repository_matches(repository, before):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request does not belong to the current repository")
    if not head_repository_matches(repository, before):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request head repository does not match origin")
    if not identity_matches(before, args.expected_head, args.expected_base, args.expected_branch):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request is not open at the expected head and base")
    if policy["pull_request"]["ready_policy"] == "keep-draft":
        return result_emit("waiting", "kept-draft", evidence, "validated pull request remains draft by policy")
    if policy["pull_request"]["ready_policy"] in ("ask", "auto") and not authorized(policy, "ready", args.authorize_ready):
        return result_emit("waiting", "waiting-user-authorization", evidence, "explicit ready authorization is required")

    pr_number = str(before["number"])
    owner_repo = repository["nameWithOwner"]

    mutated = bool(before.get("isDraft"))
    ready_result = None
    if mutated:
        pre_mutation_result = run(["gh", "pr", "view", pr_number, "--repo", owner_repo, "--json", FIELDS])
        if pre_mutation_result.returncode != 0:
            return result_emit("waiting", "waiting-external", evidence, pre_mutation_result.stderr.strip())
        pre_mutation = parse_object(pre_mutation_result)
        if pre_mutation is None:
            return result_emit("blocked", "blocked-unsafe", evidence, "pre-mutation pull-request JSON is malformed")
        evidence["pre_mutation"] = pre_mutation
        if pre_mutation != before or not repository_matches(repository, pre_mutation) or not head_repository_matches(repository, pre_mutation):
            return result_emit("blocked", "blocked-unsafe", evidence, "pull-request identity changed before ready transition")
        ready_result = run(["gh", "pr", "ready", pr_number, "--repo", owner_repo])
        evidence["ready_exit_code"] = ready_result.returncode
        evidence["ready_stdout"] = ready_result.stdout
        evidence["ready_stderr"] = ready_result.stderr

    after_result = run(["gh", "pr", "view", pr_number, "--repo", owner_repo, "--json", FIELDS])
    if after_result.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, after_result.stderr.strip())
    after = parse_object(after_result)
    if after is None:
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request verification JSON is malformed")
    evidence["after"] = after
    evidence["mutated"] = mutated
    if not repository_matches(repository, after):
        return result_emit("blocked", "blocked-unsafe", evidence, "verified pull request does not belong to the current repository")
    if not head_repository_matches(repository, after):
        return result_emit("blocked", "blocked-unsafe", evidence, "verified pull-request head repository does not match origin")
    if not identity_matches(after, args.expected_head, args.expected_base, args.expected_branch):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request identity changed during ready transition")
    if after.get("headRefName") != before.get("headRefName"):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request head branch changed during ready transition")
    if after.get("isDraft") is not False:
        blocker = ready_result.stderr.strip() if ready_result and ready_result.stderr.strip() else "GitHub did not confirm the ready transition"
        return result_emit("waiting", "waiting-external", evidence, blocker)
    if mutated and ready_result and ready_result.returncode != 0:
        evidence["mutation_attribution"] = "uncertain"
    return result_emit("passed", "ready" if mutated else "already-ready", evidence, next_stage="user-decision")


if __name__ == "__main__":
    sys.exit(main())
