#!/usr/bin/env python3
"""Recover a unique non-issue branch and pull-request lifecycle state."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.parse import urlparse


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


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


def pull_request_repositories_match(repository: dict, pull_request: dict) -> bool:
    number = pull_request.get("number")
    repository_url = (repository.get("url") or "").rstrip("/")
    head_repository = pull_request.get("headRepository")
    return (
        type(number) is int
        and number > 0
        and pull_request.get("url") == f"{repository_url}/pull/{number}"
        and pull_request.get("isCrossRepository") is False
        and isinstance(head_repository, dict)
        and (head_repository.get("nameWithOwner") or "").casefold() == (repository.get("nameWithOwner") or "").casefold()
    )


def parse_remote_head(stdout: str, branch: str) -> tuple[str | None, bool]:
    lines = [line.split() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None, True
    if len(lines) != 1 or len(lines[0]) != 2 or lines[0][1] != f"refs/heads/{branch}":
        return None, False
    return lines[0][0], True


def provenance_matches(record: dict, provenance: str) -> bool:
    lines = (record.get("body") or "").splitlines()
    origins = [line for line in lines if line.startswith("OpenCode-Origin:")]
    references = [line for line in lines if line.startswith("Refs #")]
    return origins == [f"OpenCode-Origin: {provenance}"] and not references


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
    if base != "main":
        return "blocked-unsafe", None, "non-issue lifecycle recovery requires base main"
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
    if pr.get("baseRefName") != base or not provenance_matches(pr, provenance):
        return "blocked-unsafe", None, "current branch pull-request base or provenance is invalid"
    if pr.get("state") == "MERGED":
        return "blocked-unsafe", None, "recovered merged pull request lacks durable lifecycle-owned approval and merge evidence"
    if pr.get("state") != "OPEN":
        return "blocked-unsafe", None, "current branch has a non-open pull request"
    if pr.get("headRefOid") != local_head or remote_head != local_head:
        return "blocked-unsafe", None, "local, remote, and pull-request heads differ"
    if not clean:
        return "waiting-user-cleanup", None, "local worktree contains uncommitted changes"
    next_stage = "ownership-baseline" if provenance == "cli" else "worktree-validation"
    return "open-pull-request", next_stage, None


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
    if args.base != "main":
        return emit("blocked", "blocked-unsafe", None, evidence, "non-issue lifecycle recovery requires base main")
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
    origin = run(["git", "remote", "get-url", "--all", "origin"])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", "origin"])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return emit("blocked", "blocked-unsafe", None, evidence, "origin remote identity is unavailable")
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return emit("blocked", "blocked-unsafe", None, evidence, "origin does not match the verified GitHub repository")
    listed = run(["gh", "pr", "list", "--head", branch_name, "--state", "all", "--json", "number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt,mergeCommit,isCrossRepository,headRepository"])
    if listed.returncode != 0:
        return emit("waiting", "waiting-external", None, evidence, listed.stderr.strip())
    try:
        prs = json.loads(listed.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", None, evidence, "invalid pull-request list JSON")
    if not isinstance(prs, list) or any(not isinstance(record, dict) for record in prs):
        return emit("blocked", "blocked-unsafe", None, evidence, "pull-request list shape is invalid")
    if any(not pull_request_repositories_match(repository, record) for record in prs):
        evidence["pull_requests"] = prs
        return emit("blocked", "blocked-unsafe", None, evidence, "pull-request repository identity is invalid")
    remote = run(["git", "ls-remote", "--heads", "origin", branch_name])
    if remote.returncode != 0:
        return emit("waiting", "waiting-external", None, evidence, remote.stderr.strip())
    remote_head, remote_valid = parse_remote_head(remote.stdout, branch_name)
    if not remote_valid:
        return emit("blocked", "blocked-unsafe", None, evidence, "remote branch identity is ambiguous")
    disposition, next_stage, blocker = classify(prs, remote_head, local_head, base_head, args.provenance, args.base, clean, args.expected_head)
    evidence.update({"remote_head": remote_head, "pull_requests": prs})
    status = "waiting" if disposition == "waiting-user-cleanup" else "blocked" if disposition == "blocked-unsafe" else "passed"
    return emit(status, disposition, next_stage, evidence, blocker)


if __name__ == "__main__":
    sys.exit(main())
