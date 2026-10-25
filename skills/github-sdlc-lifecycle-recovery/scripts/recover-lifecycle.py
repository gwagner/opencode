#!/usr/bin/env python3
"""Recover the unique GitHub-authoritative state of an issue lifecycle."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


VERSION = 1


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def completion_comment_matches(comment: dict, url: str, head: str) -> bool:
    lines = set((comment.get("body") or "").splitlines())
    required = {
        "Lifecycle completion: merged-pr",
        f"Pull request: {url}",
        f"Head commit: {head}",
        "Merge result: merged",
        "Delegate project-validation: passed",
        "Required checks: passed",
    }
    cleanup = {"Remote cleanup: deleted", "Remote cleanup: already-absent"}
    return required.issubset(lines) and bool(cleanup.intersection(lines))


def parse_remote_head(stdout: str, branch: str) -> tuple[str | None, bool]:
    lines = [line.split() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None, True
    expected_ref = f"refs/heads/{branch}"
    if len(lines) != 1 or len(lines[0]) != 2 or lines[0][1] != expected_ref:
        return None, False
    return lines[0][0], True


def classify(issue_state: str, prs: list[dict], remote_branch_state: str, comments: list[dict]) -> tuple[str, str | None, str | None]:
    if issue_state == "CLOSED":
        return "closed", None, None
    if issue_state != "OPEN":
        return "blocked-unsafe", None, "unsupported issue state"
    if len(prs) > 1:
        return "blocked-unsafe", None, "multiple matching pull requests"
    if not prs:
        return ("remote-branch-no-pr", "pr-publication", None) if remote_branch_state == "present-exact" else ("fresh-start", "worktree-validation", None)
    pr = prs[0]
    if any(not pr.get(key) for key in ("url", "headRefName", "headRefOid")):
        return "blocked-unsafe", None, "matching pull-request identity is incomplete"
    if pr.get("state") == "OPEN":
        if remote_branch_state != "present-exact":
            return "blocked-unsafe", None, "open pull-request remote branch is absent or unverified"
        return "open-pull-request", "hosted-checks", None
    if pr.get("state") != "MERGED":
        return "blocked-unsafe", None, "matching pull request is neither open nor merged"
    if remote_branch_state == "present-exact":
        return "merged-needs-cleanup", "remote-branch-cleanup", None
    if remote_branch_state != "already-absent":
        return "blocked-unsafe", None, "merged pull-request remote branch is unverified"
    head = pr.get("headRefOid")
    url = pr.get("url")
    current = [
        comment
        for comment in comments
        if "Lifecycle evidence: current" in (comment.get("body") or "")
        and url in (comment.get("body") or "")
        and f"Head commit: {head}" in (comment.get("body") or "")
        and "Delegate project-validation: passed" in (comment.get("body") or "")
        and "Required checks: passed" in (comment.get("body") or "")
    ]
    completion = [comment for comment in comments if completion_comment_matches(comment, url, head)]
    if not current:
        return "blocked-unsafe", None, "merged lifecycle evidence is missing"
    if not completion:
        return "merged-needs-completion", "completion-comment", None
    return "merged-needs-close", "issue-close", None


def emit(status: str, disposition: str, next_stage: str | None, evidence: dict, blocker: str | None = None) -> int:
    print(json.dumps({"version": VERSION, "status": status, "disposition": disposition, "next_stage": next_stage, "evidence": evidence, "blocker": blocker}, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    parser.add_argument("--branch")
    args = parser.parse_args()
    evidence: dict[str, object] = {}
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
    issue = run(["gh", "issue", "view", args.issue, "--json", "number,title,state,url,comments"])
    if issue.returncode != 0:
        return emit("waiting", "waiting-external", None, evidence, issue.stderr.strip())
    try:
        issue_record = json.loads(issue.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", None, evidence, "invalid issue JSON")
    if not isinstance(issue_record, dict) or not issue_record.get("number") or not issue_record.get("url") or not issue_record.get("state"):
        return emit("blocked", "blocked-unsafe", None, evidence, "issue identity is incomplete")
    evidence["issue"] = issue_record
    query = f"Refs #{issue_record['number']} in:body"
    listed = run(["gh", "pr", "list", "--search", query, "--state", "all", "--limit", "100", "--json", "number,state,url,title,body,baseRefName,headRefName,headRefOid,mergedAt"])
    if listed.returncode != 0:
        return emit("waiting", "waiting-external", None, evidence, listed.stderr.strip())
    try:
        candidates = json.loads(listed.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", None, evidence, "invalid pull-request list JSON")
    if not isinstance(candidates, list) or any(not isinstance(record, dict) for record in candidates):
        return emit("blocked", "blocked-unsafe", None, evidence, "pull-request list shape is invalid")
    marker = f"Refs #{issue_record['number']}"
    issue_matches = [record for record in candidates if marker in (record.get("body") or "").splitlines() and record.get("baseRefName") == "main"]
    provenance_marker = "OpenCode-Origin: github-issue"
    invalid_provenance = [record for record in issue_matches if provenance_marker not in (record.get("body") or "").splitlines()]
    if invalid_provenance:
        evidence["pull_requests"] = issue_matches
        return emit("blocked", "blocked-unsafe", None, evidence, "matching pull-request provenance is invalid")
    prs = issue_matches
    remote_branch_state = "not-applicable"
    branch = args.branch
    if len(prs) == 1 and prs[0].get("headRefName"):
        pull_request_branch = prs[0]["headRefName"]
        if args.branch and args.branch != pull_request_branch:
            evidence["pull_requests"] = prs
            evidence["supplied_branch"] = args.branch
            evidence["pull_request_branch"] = pull_request_branch
            return emit("blocked", "blocked-unsafe", None, evidence, "supplied branch conflicts with the matching pull request")
        branch = pull_request_branch
    if branch:
        remote = run(["git", "ls-remote", "--heads", "origin", branch])
        if remote.returncode != 0:
            return emit("waiting", "waiting-external", None, evidence, remote.stderr.strip())
        remote_head, remote_valid = parse_remote_head(remote.stdout, branch)
        if not remote_valid:
            return emit("blocked", "blocked-unsafe", None, evidence, "remote branch identity is ambiguous")
        remote_branch_state = "present-exact" if remote_head else "already-absent"
        evidence["branch"] = branch
        evidence["remote_head"] = remote_head
        if remote_head:
            local = run(["git", "rev-parse", "HEAD"])
            evidence["local_head"] = local.stdout.strip() if local.returncode == 0 else None
            if not prs and (local.returncode != 0 or local.stdout.strip() != remote_head):
                return emit("blocked", "blocked-unsafe", None, evidence, "local and remote branch heads differ without a matching pull request")
            if prs and remote_head != prs[0].get("headRefOid"):
                return emit("blocked", "blocked-unsafe", None, evidence, "remote branch no longer points to the pull-request head")
    disposition, next_stage, blocker = classify(issue_record.get("state"), prs, remote_branch_state, issue_record.get("comments") or [])
    evidence["pull_requests"] = prs
    evidence["remote_branch_state"] = remote_branch_state
    if prs and prs[0].get("state") == "MERGED" and remote_branch_state == "already-absent":
        evidence["cleanup_disposition"] = "already-absent"
    status = "passed" if disposition not in ("blocked-unsafe",) else "blocked"
    return emit(status, disposition, next_stage, evidence, blocker)


if __name__ == "__main__":
    sys.exit(main())
