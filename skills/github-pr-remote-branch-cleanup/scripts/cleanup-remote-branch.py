#!/usr/bin/env python3
"""Delete only an unchanged remote branch for one verified merged PR."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.parse import urlparse


VERSION = 1
FIELDS = "number,url,state,body,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def emit(status: str, disposition: str, evidence: dict, blocker: str | None = None) -> int:
    print(json.dumps({
        "version": VERSION,
        "status": status,
        "disposition": disposition,
        "next_stage": "completion" if status == "passed" else None,
        "evidence": evidence,
        "blocker": blocker,
    }, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


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


def parse_remote_head(stdout: str, branch: str | None = None) -> tuple[str | None, bool]:
    lines = [line.split() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None, True
    if len(lines) != 1 or len(lines[0]) != 2:
        return None, False
    if branch and lines[0][1] != f"refs/heads/{branch}":
        return None, False
    return lines[0][0], True


def merged_identity_matches(record: dict, head: str, base: str, provenance: str) -> bool:
    return (
        record.get("state") == "MERGED"
        and record.get("headRefOid") == head
        and record.get("baseRefName") == base
        and bool(record.get("number"))
        and bool(record.get("url"))
        and bool(record.get("headRefName"))
        and f"OpenCode-Origin: {provenance}" in (record.get("body") or "").splitlines()
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--expected-base", default="main")
    parser.add_argument("--provenance", choices=("cli", "openchamber", "github-issue"), required=True)
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

    viewed = run(["gh", "pr", "view", args.pr, "--json", FIELDS])
    if viewed.returncode != 0:
        return emit("waiting", "waiting-external", evidence, viewed.stderr.strip())
    pull_request = parse_record(viewed)
    if pull_request is None:
        return emit("blocked", "blocked-unsafe", evidence, "pull-request JSON is malformed")
    evidence["pull_request"] = pull_request
    if not repository_matches(repository, pull_request):
        return emit("blocked", "blocked-unsafe", evidence, "pull request does not belong to the current repository")
    if not head_repository_matches(repository, pull_request):
        return emit("blocked", "blocked-unsafe", evidence, "pull request head repository does not match origin")
    if not merged_identity_matches(pull_request, args.expected_head, args.expected_base, args.provenance):
        return emit("blocked", "blocked-unsafe", evidence, "pull request failed the merged-branch cleanup gate")
    branch = pull_request["headRefName"]
    if branch == args.expected_base:
        return emit("blocked", "blocked-unsafe", evidence, "refusing to delete the base branch")

    before = run(["git", "ls-remote", "--heads", "origin", branch])
    if before.returncode != 0:
        return emit("waiting", "waiting-external", evidence, before.stderr.strip())
    remote_head, valid = parse_remote_head(before.stdout, branch)
    evidence["remote_head_before"] = remote_head
    if not valid:
        return emit("blocked", "blocked-unsafe", evidence, "remote branch identity is ambiguous")
    if remote_head is None:
        return emit("passed", "already-absent", evidence)
    if remote_head != args.expected_head:
        return emit("blocked", "blocked-unsafe", evidence, "remote branch no longer points to the merged head")

    lease = f"--force-with-lease=refs/heads/{branch}:{args.expected_head}"
    deleted = run(["git", "push", lease, "--delete", "origin", branch])
    evidence["delete_lease"] = lease
    evidence["delete_exit_code"] = deleted.returncode
    evidence["delete_stdout"] = deleted.stdout
    evidence["delete_stderr"] = deleted.stderr
    after = run(["git", "ls-remote", "--heads", "origin", branch])
    if after.returncode != 0:
        return emit("waiting", "waiting-external", evidence, after.stderr.strip())
    remaining_head, remaining_valid = parse_remote_head(after.stdout, branch)
    evidence["remote_head_after"] = remaining_head
    if not remaining_valid or remaining_head not in (None, args.expected_head):
        return emit("blocked", "blocked-unsafe", evidence, "remote branch changed during deletion")
    if remaining_head is not None:
        return emit("waiting", "waiting-external", evidence, deleted.stderr.strip() or "remote branch deletion was not confirmed")
    return emit("passed", "deleted", evidence)


if __name__ == "__main__":
    sys.exit(main())
