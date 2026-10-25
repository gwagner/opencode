#!/usr/bin/env python3
"""Recover the unique GitHub-authoritative state of an issue lifecycle."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_pr_lifecycle_common import (
    emit as result_emit,
    head_repository_matches,
    marker_matches,
    parse_remote_head,
    remote_urls_match,
    repository_matches,
    run,
)
from urllib.parse import urlparse


VERSION = 1



def comment_author_matches(comment: dict, actor: str) -> bool:
    author = comment.get("author")
    return isinstance(author, dict) and (author.get("login") or "").casefold() == actor.casefold()


def exact_controlled_line(lines: list[str], prefix: str, expected: str) -> bool:
    return [line for line in lines if line.startswith(prefix)] == [expected]


def visual_evidence_matches(lines: list[str]) -> bool:
    visual = [line for line in lines if line.startswith("Visual evidence:")]
    if visual == ["Visual evidence: not required"]:
        return not any(line.startswith("![Before:") or line.startswith("![After:") for line in lines)
    if visual != ["Visual evidence: passed"]:
        return False
    before = [line for line in lines if line.startswith("![Before:")]
    after = [line for line in lines if line.startswith("![After:")]
    if len(before) != 1 or len(after) != 1:
        return False
    before_match = re.fullmatch(r"!\[Before: ([^\]]+)\]\((https://[^)]+)\)", before[0])
    after_match = re.fullmatch(r"!\[After: ([^\]]+)\]\((https://[^)]+)\)", after[0])
    if before_match is None or after_match is None or before_match.group(1) != after_match.group(1):
        return False
    urls = (urlparse(before_match.group(2)), urlparse(after_match.group(2)))
    return all(url.hostname == "github.com" and url.path.startswith("/user-attachments/") for url in urls)


def current_comment_matches(comment: dict, url: str, head: str, actor: str) -> bool:
    lines = (comment.get("body") or "").splitlines()
    delivered = [line for line in lines if line.startswith("Delivered outcome:")]
    return (
        comment_author_matches(comment, actor)
        and exact_controlled_line(lines, "Lifecycle evidence:", "Lifecycle evidence: current")
        and len(delivered) == 1
        and bool(delivered[0].removeprefix("Delivered outcome:").strip())
        and exact_controlled_line(lines, "Pull request:", f"Pull request: {url}")
        and exact_controlled_line(lines, "Head commit:", f"Head commit: {head}")
        and exact_controlled_line(lines, "Delegate project-validation:", "Delegate project-validation: passed")
        and exact_controlled_line(lines, "Required checks:", "Required checks: passed")
        and visual_evidence_matches(lines)
    )


def completion_comment_matches(comment: dict, url: str, head: str, actor: str) -> bool:
    lines = (comment.get("body") or "").splitlines()
    cleanup = {"Remote cleanup: deleted", "Remote cleanup: already-absent"}
    return (
        comment_author_matches(comment, actor)
        and exact_controlled_line(lines, "Lifecycle completion:", "Lifecycle completion: merged-pr")
        and exact_controlled_line(lines, "Pull request:", f"Pull request: {url}")
        and exact_controlled_line(lines, "Head commit:", f"Head commit: {head}")
        and exact_controlled_line(lines, "Merge result:", "Merge result: merged")
        and exact_controlled_line(lines, "Delegate project-validation:", "Delegate project-validation: passed")
        and exact_controlled_line(lines, "Required checks:", "Required checks: passed")
        and sum(line in cleanup for line in lines) == 1
        and len([line for line in lines if line.startswith("Remote cleanup:")]) == 1
    )


def issue_repository_matches(repository: dict, issue: dict) -> bool:
    number = issue.get("number")
    repository_url = (repository.get("url") or "").rstrip("/")
    return (
        bool(repository.get("nameWithOwner"))
        and bool(repository_url)
        and type(number) is int
        and number > 0
        and issue.get("url") == f"{repository_url}/issues/{number}"
    )



def classify(issue_state: str, prs: list[dict], remote_branch_state: str, comments: list[dict], actor: str) -> tuple[str, str | None, str | None]:
    if issue_state not in ("OPEN", "CLOSED"):
        return "blocked-unsafe", None, "unsupported issue state"
    if len(prs) > 1:
        return "blocked-unsafe", None, "multiple matching pull requests"
    if not prs:
        if issue_state == "CLOSED":
            return "blocked-unsafe", None, "closed issue has no matching merged pull request"
        return ("remote-branch-no-pr", "worktree-validation", None) if remote_branch_state == "present-exact" else ("fresh-start", "worktree-validation", None)
    pr = prs[0]
    if any(not pr.get(key) for key in ("url", "headRefName", "headRefOid")):
        return "blocked-unsafe", None, "matching pull-request identity is incomplete"
    if pr.get("state") == "OPEN":
        if issue_state == "CLOSED":
            return "blocked-unsafe", None, "closed issue still has an open pull request"
        if remote_branch_state != "present-exact":
            return "blocked-unsafe", None, "open pull-request remote branch is absent or unverified"
        return "open-pull-request", "worktree-validation", None
    if pr.get("state") != "MERGED":
        return "blocked-unsafe", None, "matching pull request is neither open nor merged"
    merge_commit = pr.get("mergeCommit")
    if not isinstance(merge_commit, dict) or not merge_commit.get("oid"):
        return "blocked-unsafe", None, "merged pull-request merge commit is missing"
    if remote_branch_state == "present-exact":
        return "blocked-unsafe", None, "recovered merged pull request lacks durable lifecycle-owned approval and merge evidence"
    if remote_branch_state != "already-absent":
        return "blocked-unsafe", None, "merged pull-request remote branch is unverified"
    head = pr.get("headRefOid")
    url = pr.get("url")
    current = [comment for comment in comments if current_comment_matches(comment, url, head, actor)]
    completion = [comment for comment in comments if completion_comment_matches(comment, url, head, actor)]
    if len({comment.get("body") or "" for comment in current}) > 1:
        return "blocked-unsafe", None, "current lifecycle evidence conflicts"
    if len({comment.get("body") or "" for comment in completion}) > 1:
        return "blocked-unsafe", None, "completion lifecycle evidence conflicts"
    if not current:
        return "blocked-unsafe", None, "merged lifecycle evidence is missing"
    if not completion:
        return "blocked-unsafe", None, "recovered merge lacks exact lifecycle completion evidence"
    if issue_state == "CLOSED":
        return "closed", None, None
    return "merged-needs-close", "issue-close", None



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    parser.add_argument("--branch")
    parser.add_argument("--validated-head")
    args = parser.parse_args()
    evidence: dict[str, object] = {}
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
    origin = run(["git", "remote", "get-url", "--all", "origin"])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", "origin"])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return result_emit("blocked", "blocked-unsafe", evidence, "origin remote identity is unavailable", None)
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return result_emit("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository", None)
    repository_host = urlparse(repository["url"]).hostname
    if not repository_host:
        return result_emit("blocked", "blocked-unsafe", evidence, "repository host is missing", None)
    actor_result = run(["gh", "api", "--hostname", repository_host, "user", "--jq", ".login"])
    if actor_result.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, actor_result.stderr.strip())
    actor = actor_result.stdout.strip()
    if not actor:
        return result_emit("blocked", "blocked-unsafe", evidence, "authenticated GitHub actor is missing", None)
    evidence["actor"] = actor
    issue = run(["gh", "issue", "view", args.issue, "--repo", repository["nameWithOwner"], "--json", "number,title,state,url,comments"])
    if issue.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, issue.stderr.strip())
    try:
        issue_record = json.loads(issue.stdout)
    except json.JSONDecodeError:
        return result_emit("blocked", "blocked-unsafe", evidence, "invalid issue JSON", None)
    if not isinstance(issue_record, dict) or not issue_record.get("number") or not issue_record.get("url") or not issue_record.get("state"):
        return result_emit("blocked", "blocked-unsafe", evidence, "issue identity is incomplete", None)
    comments = issue_record.get("comments")
    if not isinstance(comments, list) or any(not isinstance(comment, dict) or not isinstance(comment.get("body"), str) for comment in comments):
        return result_emit("blocked", "blocked-unsafe", evidence, "issue comment shape is invalid", None)
    evidence["issue"] = issue_record
    if not issue_repository_matches(repository, issue_record):
        return result_emit("blocked", "blocked-unsafe", evidence, "issue does not belong to the current repository", None)
    query = f"Refs #{issue_record['number']} in:body"
    listed = run(["gh", "pr", "list", "--repo", repository["nameWithOwner"], "--search", query, "--state", "all", "--limit", "100", "--json", "number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt,mergeCommit,isCrossRepository,headRepository"])
    if listed.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, listed.stderr.strip())
    try:
        candidates = json.loads(listed.stdout)
    except json.JSONDecodeError:
        return result_emit("blocked", "blocked-unsafe", evidence, "invalid pull-request list JSON", None)
    if not isinstance(candidates, list) or any(not isinstance(record, dict) for record in candidates):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull-request list shape is invalid", None)
    marker = f"Refs #{issue_record['number']}"
    issue_matches = [record for record in candidates if marker in (record.get("body") or "").splitlines()]
    wrong_base = [record for record in issue_matches if record.get("baseRefName") != "main"]
    if wrong_base:
        evidence["pull_requests"] = issue_matches
        return result_emit("blocked", "blocked-unsafe", evidence, "matching pull-request base is invalid", None)
    invalid_markers = [record for record in issue_matches if not marker_matches(record, "github-issue", str(issue_record["number"]))]
    if invalid_markers:
        evidence["pull_requests"] = issue_matches
        return result_emit("blocked", "blocked-unsafe", evidence, "matching pull-request lifecycle markers are conflicting or invalid", None)
    prs = issue_matches
    if any(not (repository_matches(repository, record) and head_repository_matches(repository, record)) for record in prs):
        evidence["pull_requests"] = prs
        return result_emit("blocked", "blocked-unsafe", evidence, "matching pull-request repository identity is invalid", None)
    remote_branch_state = "not-applicable"
    branch = args.branch
    if len(prs) == 1 and prs[0].get("headRefName"):
        pull_request_branch = prs[0]["headRefName"]
        if args.branch and args.branch != pull_request_branch:
            evidence["pull_requests"] = prs
            evidence["supplied_branch"] = args.branch
            evidence["pull_request_branch"] = pull_request_branch
            return result_emit("blocked", "blocked-unsafe", evidence, "supplied branch conflicts with the matching pull request", None)
        branch = pull_request_branch
    if branch:
        remote = run(["git", "ls-remote", "--heads", "origin", branch])
        if remote.returncode != 0:
            return result_emit("waiting", "waiting-external", evidence, remote.stderr.strip())
        remote_head, remote_valid = parse_remote_head(remote.stdout, branch)
        if not remote_valid:
            return result_emit("blocked", "blocked-unsafe", evidence, "remote branch identity is ambiguous", None)
        remote_branch_state = "present-exact" if remote_head else "already-absent"
        evidence["branch"] = branch
        evidence["remote_head"] = remote_head
        if remote_head:
            local = run(["git", "rev-parse", "HEAD"])
            evidence["local_head"] = local.stdout.strip() if local.returncode == 0 else None
            if not prs:
                current_branch = run(["git", "branch", "--show-current"])
                evidence["current_branch"] = current_branch.stdout.strip() if current_branch.returncode == 0 else None
                evidence["validated_head"] = args.validated_head
                if current_branch.returncode != 0 or current_branch.stdout.strip() != branch:
                    return result_emit("blocked", "blocked-unsafe", evidence, "supplied branch is not the current local branch", None)
                status_result = run(["git", "status", "--porcelain=v1"])
                if status_result.returncode != 0:
                    return result_emit("blocked", "blocked-unsafe", evidence, "local worktree state is unavailable", None)
                if status_result.stdout:
                    return result_emit("waiting", "waiting-user-cleanup", evidence, "local worktree contains uncommitted changes", None)
                if local.returncode != 0 or local.stdout.strip() != remote_head:
                    return result_emit("blocked", "blocked-unsafe", evidence, "local and remote branch heads differ without a matching pull request", None)
                if args.validated_head != remote_head:
                    return result_emit("blocked", "blocked-unsafe", evidence, "remote branch without a pull request lacks retained validated-head evidence", None)
            if prs and remote_head != prs[0].get("headRefOid"):
                return result_emit("blocked", "blocked-unsafe", evidence, "remote branch no longer points to the pull-request head", None)
    disposition, next_stage, blocker = classify(issue_record.get("state"), prs, remote_branch_state, comments, actor)
    evidence["pull_requests"] = prs
    evidence["remote_branch_state"] = remote_branch_state
    if prs and prs[0].get("state") == "MERGED" and remote_branch_state == "already-absent":
        evidence["cleanup_disposition"] = "already-absent"
    status = "passed" if disposition not in ("blocked-unsafe",) else "blocked"
    return result_emit(status, disposition, evidence, blocker, next_stage)


if __name__ == "__main__":
    sys.exit(main())
