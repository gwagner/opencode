#!/usr/bin/env python3
"""Delete only an unchanged remote branch for one verified merged PR."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_authorization_argument, add_policy_argument, authorized, load_policy, policy_evidence
from github_pr_lifecycle_common import (
    emit as result_emit,
    head_repository_matches,
    marker_matches,
    parse_object,
    parse_remote_head,
    remote_urls_match,
    repository_matches,
    run,
)
FIELDS = "number,url,state,body,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"




def merged_identity_matches(record: dict, head: str, base: str, provenance: str, issue: str | None = None) -> bool:
    markers_match = marker_matches(record, provenance, issue)
    return (
        record.get("state") == "MERGED"
        and record.get("headRefOid") == head
        and record.get("baseRefName") == base
        and bool(record.get("number"))
        and bool(record.get("url"))
        and bool(record.get("headRefName"))
        and markers_match
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-base", default=None)
    parser.add_argument("--provenance", required=True)
    parser.add_argument("--issue")
    add_policy_argument(parser)
    add_authorization_argument(parser, "cleanup")
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy)
    except ValueError as exc:
        return result_emit("blocked", "blocked-unsafe", {}, str(exc))
    if args.expected_base is None:
        args.expected_base = policy["base_branch"]
    evidence: dict[str, object] = policy_evidence(policy)
    if policy["remote_cleanup"] == "retain":
        return result_emit("passed", "retained", evidence, next_stage="completion")
    if not authorized(policy, "cleanup", args.authorize_cleanup):
        return result_emit("blocked", "blocked-unsafe", evidence, "explicit cleanup authorization is required")
    if args.provenance not in policy["provenance"]:
        return result_emit("blocked", "blocked-unsafe", evidence, "provenance is not permitted by policy")
    if (args.provenance == "github-issue") != bool(args.issue) or (args.issue and not args.issue.lstrip("#").isdigit()):
        return result_emit("blocked", "blocked-unsafe", evidence, "numeric issue identity is required only for github-issue provenance")

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

    viewed = run(["gh", "pr", "view", args.pr, "--repo", repository["nameWithOwner"], "--json", FIELDS])
    if viewed.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, viewed.stderr.strip())
    pull_request = parse_object(viewed)
    if pull_request is None:
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request JSON is malformed")
    evidence["pull_request"] = pull_request
    if not repository_matches(repository, pull_request):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request does not belong to the current repository")
    if not head_repository_matches(repository, pull_request):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request head repository does not match origin")
    if not merged_identity_matches(pull_request, args.expected_head, args.expected_base, args.provenance, args.issue):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request failed the merged-branch cleanup gate")
    branch = pull_request["headRefName"]
    if branch == args.expected_base:
        return result_emit("blocked", "blocked-unsafe", evidence, "refusing to delete the base branch")

    before = run(["git", "ls-remote", "--heads", policy["remote"], branch])
    if before.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, before.stderr.strip())
    remote_head, valid = parse_remote_head(before.stdout, branch)
    evidence["remote_head_before"] = remote_head
    if not valid:
        return result_emit("blocked", "blocked-unsafe", evidence, "remote branch identity is ambiguous")
    if remote_head is None:
        return result_emit("passed", "already-absent", evidence, next_stage="completion")
    if remote_head != args.expected_head:
        return result_emit("blocked", "blocked-unsafe", evidence, "remote branch no longer points to the merged head")

    lease = f"--force-with-lease=refs/heads/{branch}:{args.expected_head}"
    deleted = run(["git", "push", lease, "--delete", policy["remote"], branch])
    evidence["delete_lease"] = lease
    evidence["delete_exit_code"] = deleted.returncode
    evidence["delete_stdout"] = deleted.stdout
    evidence["delete_stderr"] = deleted.stderr
    after = run(["git", "ls-remote", "--heads", policy["remote"], branch])
    if after.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, after.stderr.strip())
    remaining_head, remaining_valid = parse_remote_head(after.stdout, branch)
    evidence["remote_head_after"] = remaining_head
    if not remaining_valid or remaining_head not in (None, args.expected_head):
        return result_emit("blocked", "blocked-unsafe", evidence, "remote branch changed during deletion")
    if remaining_head is not None:
        return result_emit("waiting", "waiting-external", evidence, deleted.stderr.strip() or "remote branch deletion was not confirmed")
    if deleted.returncode != 0:
        return result_emit("passed", "already-absent", evidence, next_stage="completion")
    return result_emit("passed", "deleted", evidence, next_stage="completion")


if __name__ == "__main__":
    sys.exit(main())
