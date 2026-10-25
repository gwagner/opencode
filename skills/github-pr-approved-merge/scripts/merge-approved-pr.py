#!/usr/bin/env python3
"""Verify one explicitly approved pull request was manually squash-merged."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_pr_lifecycle_common import (
    emit as result_emit,
    head_repository_matches,
    parse_object,
    remote_urls_match,
    repository_matches,
    run,
)
FIELDS = "number,url,state,isDraft,mergeable,baseRefName,headRefName,headRefOid,mergedAt,mergeCommit,isCrossRepository,headRepository"




def identity_matches(record: dict, expected_head: str, expected_base: str, expected_branch: str) -> bool:
    return (
        record.get("headRefOid") == expected_head
        and record.get("baseRefName") == expected_base
        and record.get("headRefName") == expected_branch
        and bool(record.get("number"))
        and bool(record.get("url"))
        and bool(record.get("headRefName"))
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-branch", required=True)
    parser.add_argument("--expected-base", default="main")
    args = parser.parse_args()
    evidence: dict[str, object] = {}

    auth = run(["gh", "auth", "status"])
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    if auth.returncode != 0 or repo.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, (auth.stderr or repo.stderr).strip())
    repository = parse_object(repo)
    if not repository or not repository.get("nameWithOwner") or not repository.get("url"):
        return result_emit("blocked", "blocked-unsafe", evidence, "repository identity is malformed or incomplete")
    evidence["repository"] = repository

    origin = run(["git", "remote", "get-url", "--all", "origin"])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", "origin"])
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
    if not identity_matches(pull_request, args.expected_head, args.expected_base, args.expected_branch):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request identity does not match the approved manual merge")
    if pull_request.get("isDraft") is not False:
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request is not ready")
    if pull_request.get("state") == "OPEN":
        if pull_request.get("mergeable") != "MERGEABLE":
            return result_emit("blocked", "blocked-unsafe", evidence, "open pull request is no longer mergeable")
        return result_emit("waiting", "waiting-user-merge", evidence, "manually squash-merge the exact pull request in GitHub and confirm in the current turn")
    if pull_request.get("state") != "MERGED":
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request is neither open nor merged")
    merge_commit = pull_request.get("mergeCommit")
    if not pull_request.get("mergedAt") or not isinstance(merge_commit, dict) or not merge_commit.get("oid"):
        return result_emit("blocked", "blocked-unsafe", evidence, "verified merge evidence is incomplete")
    return result_emit("passed", "user-merged", evidence, next_stage="remote-branch-cleanup")


if __name__ == "__main__":
    sys.exit(main())
