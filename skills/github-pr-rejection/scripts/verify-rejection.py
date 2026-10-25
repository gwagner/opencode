#!/usr/bin/env python3
"""Verify the non-mutating terminal result of an exact-head PR rejection."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.parse import urlparse


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def matches(record: dict, head: str, base: str, branch: str) -> bool:
    return record.get("state") == "OPEN" and record.get("headRefOid") == head and record.get("baseRefName") == base and record.get("headRefName") == branch


def repository_matches(repository: dict, pull_request: dict) -> bool:
    number = pull_request.get("number")
    repository_url = (repository.get("url") or "").rstrip("/")
    return (
        bool(repository.get("nameWithOwner"))
        and bool(repository_url)
        and type(number) is int
        and number > 0
        and pull_request.get("url") == f"{repository_url}/pull/{number}"
    )


def remote_repository_matches(repository: dict, remote_url: str) -> bool:
    expected_url = urlparse(repository.get("url") or "")
    expected_name = (repository.get("nameWithOwner") or "").strip("/")
    remote_url = remote_url.strip()
    if "://" in remote_url:
        parsed = urlparse(remote_url)
        host = parsed.hostname or ""
        path = parsed.path
    elif ":" in remote_url:
        host_part, path = remote_url.split(":", 1)
        host = host_part.rsplit("@", 1)[-1]
    else:
        return False
    remote_name = path.strip("/")
    if remote_name.endswith(".git"):
        remote_name = remote_name[:-4]
    return bool(expected_url.hostname and expected_name) and host.casefold() == expected_url.hostname.casefold() and remote_name.casefold() == expected_name.casefold()


def remote_urls_match(repository: dict, remote_urls: str) -> bool:
    urls = [url for url in remote_urls.splitlines() if url.strip()]
    return bool(urls) and all(remote_repository_matches(repository, url) for url in urls)


def head_repository_matches(repository: dict, pull_request: dict) -> bool:
    head_repository = pull_request.get("headRepository")
    return (
        pull_request.get("isCrossRepository") is False
        and isinstance(head_repository, dict)
        and (head_repository.get("nameWithOwner") or "").casefold() == (repository.get("nameWithOwner") or "").casefold()
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
        print(json.dumps({"version": 1, "status": "waiting", "disposition": "waiting-external", "next_stage": "user-decision", "evidence": evidence, "blocker": (auth.stderr or repo.stderr).strip()}, sort_keys=True))
        return 3
    try:
        evidence["repository"] = json.loads(repo.stdout)
    except json.JSONDecodeError:
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": None, "evidence": evidence, "blocker": "invalid repository JSON"}, sort_keys=True))
        return 2
    repository = evidence["repository"]
    if not isinstance(repository, dict) or not repository.get("nameWithOwner") or not repository.get("url"):
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": None, "evidence": evidence, "blocker": "repository identity is incomplete"}, sort_keys=True))
        return 2
    origin = run(["git", "remote", "get-url", "--all", "origin"])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", "origin"])
    if origin.returncode != 0 or push_origin.returncode != 0 or not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": None, "evidence": evidence, "blocker": "origin does not match the verified GitHub repository"}, sort_keys=True))
        return 2
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    viewed = run(["gh", "pr", "view", args.pr, "--repo", repository["nameWithOwner"], "--json", "number,url,state,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"])
    if viewed.returncode != 0:
        print(json.dumps({"version": 1, "status": "waiting", "disposition": "waiting-external", "next_stage": "user-decision", "evidence": evidence, "blocker": viewed.stderr.strip()}, sort_keys=True))
        return 3
    try:
        evidence["pull_request"] = json.loads(viewed.stdout)
    except json.JSONDecodeError:
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": None, "evidence": evidence, "blocker": "invalid pull-request JSON"}, sort_keys=True))
        return 2
    pull_request = evidence["pull_request"]
    if not isinstance(pull_request, dict) or not repository_matches(repository, pull_request) or not head_repository_matches(repository, pull_request):
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": "user-decision", "evidence": evidence, "blocker": "pull request does not belong to the current repository"}, sort_keys=True))
        return 2
    if not matches(pull_request, args.expected_head, args.expected_base, args.expected_branch):
        print(json.dumps({"version": 1, "status": "blocked", "disposition": "blocked-unsafe", "next_stage": "user-decision", "evidence": evidence, "blocker": "pull request changed after rejection"}, sort_keys=True))
        return 2
    print(json.dumps({"version": 1, "status": "passed", "disposition": "rejected-open-pr", "next_stage": None, "evidence": evidence, "blocker": None}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
