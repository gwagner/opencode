#!/usr/bin/env python3
"""Idempotently mark one exact open pull request ready for review."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.parse import urlparse


VERSION = 1
FIELDS = "number,url,state,isDraft,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def emit(status: str, disposition: str, evidence: dict, blocker: str | None = None) -> int:
    print(json.dumps({
        "version": VERSION,
        "status": status,
        "disposition": disposition,
        "next_stage": "user-decision" if status == "passed" else None,
        "evidence": evidence,
        "blocker": blocker,
    }, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


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


def parse_record(completed: subprocess.CompletedProcess[str]) -> dict | None:
    if completed.returncode != 0:
        return None
    try:
        record = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return record if isinstance(record, dict) else None


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
        return emit("waiting", "waiting-external", evidence, (auth.stderr or repo.stderr).strip())
    repository = parse_record(repo)
    if not repository or not repository.get("nameWithOwner") or not repository.get("url"):
        return emit("blocked", "blocked-unsafe", evidence, "repository identity is malformed or incomplete")
    evidence["repository"] = repository

    origin = run(["git", "remote", "get-url", "--all", "origin"])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", "origin"])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return emit("blocked", "blocked-unsafe", evidence, "origin remote identity is unavailable")
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return emit("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository")

    before_result = run(["gh", "pr", "view", args.pr, "--json", FIELDS])
    if before_result.returncode != 0:
        return emit("waiting", "waiting-external", evidence, before_result.stderr.strip())
    before = parse_record(before_result)
    if before is None:
        return emit("blocked", "blocked-unsafe", evidence, "pull-request JSON is malformed")
    evidence["before"] = before
    if not repository_matches(repository, before):
        return emit("blocked", "blocked-unsafe", evidence, "pull request does not belong to the current repository")
    if not head_repository_matches(repository, before):
        return emit("blocked", "blocked-unsafe", evidence, "pull request head repository does not match origin")
    if not identity_matches(before, args.expected_head, args.expected_base, args.expected_branch):
        return emit("blocked", "blocked-unsafe", evidence, "pull request is not open at the expected head and base")

    pr_number = str(before["number"])
    owner_repo = repository["nameWithOwner"]

    mutated = bool(before.get("isDraft"))
    ready_result = None
    if mutated:
        pre_mutation_result = run(["gh", "pr", "view", pr_number, "--repo", owner_repo, "--json", FIELDS])
        if pre_mutation_result.returncode != 0:
            return emit("waiting", "waiting-external", evidence, pre_mutation_result.stderr.strip())
        pre_mutation = parse_record(pre_mutation_result)
        if pre_mutation is None:
            return emit("blocked", "blocked-unsafe", evidence, "pre-mutation pull-request JSON is malformed")
        evidence["pre_mutation"] = pre_mutation
        if pre_mutation != before or not repository_matches(repository, pre_mutation) or not head_repository_matches(repository, pre_mutation):
            return emit("blocked", "blocked-unsafe", evidence, "pull-request identity changed before ready transition")
        ready_result = run(["gh", "pr", "ready", pr_number, "--repo", owner_repo])
        evidence["ready_exit_code"] = ready_result.returncode
        evidence["ready_stdout"] = ready_result.stdout
        evidence["ready_stderr"] = ready_result.stderr

    after_result = run(["gh", "pr", "view", pr_number, "--repo", owner_repo, "--json", FIELDS])
    if after_result.returncode != 0:
        return emit("waiting", "waiting-external", evidence, after_result.stderr.strip())
    after = parse_record(after_result)
    if after is None:
        return emit("blocked", "blocked-unsafe", evidence, "pull-request verification JSON is malformed")
    evidence["after"] = after
    evidence["mutated"] = mutated
    if not repository_matches(repository, after):
        return emit("blocked", "blocked-unsafe", evidence, "verified pull request does not belong to the current repository")
    if not head_repository_matches(repository, after):
        return emit("blocked", "blocked-unsafe", evidence, "verified pull-request head repository does not match origin")
    if not identity_matches(after, args.expected_head, args.expected_base, args.expected_branch):
        return emit("blocked", "blocked-unsafe", evidence, "pull-request identity changed during ready transition")
    if after.get("headRefName") != before.get("headRefName"):
        return emit("blocked", "blocked-unsafe", evidence, "pull-request head branch changed during ready transition")
    if after.get("isDraft") is not False:
        blocker = ready_result.stderr.strip() if ready_result and ready_result.stderr.strip() else "GitHub did not confirm the ready transition"
        return emit("waiting", "waiting-external", evidence, blocker)
    if mutated and ready_result and ready_result.returncode != 0:
        return emit("blocked", "blocked-unsafe", evidence, "pull request became ready after the ready command failed")
    return emit("passed", "ready" if mutated else "already-ready", evidence)


if __name__ == "__main__":
    sys.exit(main())
