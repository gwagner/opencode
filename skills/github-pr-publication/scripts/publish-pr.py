#!/usr/bin/env python3
"""Idempotently push the current head and create or update one draft PR."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from urllib.parse import urlparse


VERSION = 1


def run(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, input=input_text, text=True, capture_output=True, check=False)


def result(status: str, disposition: str, evidence: dict, blocker: str | None = None, next_stage: str | None = None) -> int:
    print(json.dumps({
        "version": VERSION,
        "status": status,
        "disposition": disposition,
        "next_stage": next_stage,
        "evidence": evidence,
        "blocker": blocker,
    }, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 2


def canonical_body(provenance: str, body: str, issue: str | None) -> str:
    lines = [body.rstrip(), "", f"OpenCode-Origin: {provenance}"]
    if provenance == "github-issue":
        lines.append(f"Refs #{issue.lstrip('#') if issue else ''}")
    return "\n".join(lines).rstrip() + "\n"


def has_reserved_markers(body: str) -> bool:
    return any(line.startswith("OpenCode-Origin:") or line.startswith("Refs #") for line in body.splitlines())


def provenance_matches(record: dict, provenance: str, issue: str | None) -> bool:
    lines = (record.get("body") or "").splitlines()
    origins = [line for line in lines if line.startswith("OpenCode-Origin:")]
    references = [line for line in lines if line.startswith("Refs #")]
    if origins != [f"OpenCode-Origin: {provenance}"]:
        return False
    if provenance == "github-issue":
        return references == [f"Refs #{issue.lstrip('#') if issue else ''}"]
    return not references


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


def pull_request_identity_matches(repository: dict, record: dict, base: str, branch: str) -> bool:
    number = record.get("number")
    repository_url = (repository.get("url") or "").rstrip("/")
    head_repository = record.get("headRepository")
    return (
        type(number) is int
        and number > 0
        and record.get("url") == f"{repository_url}/pull/{number}"
        and record.get("baseRefName") == base
        and record.get("headRefName") == branch
        and record.get("isCrossRepository") is False
        and isinstance(head_repository, dict)
        and (head_repository.get("nameWithOwner") or "").casefold() == (repository.get("nameWithOwner") or "").casefold()
    )


def select_pull_request(records: list[dict], repository: dict, provenance: str, issue: str | None, base: str, branch: str) -> tuple[str, dict | None]:
    if len(records) > 1:
        return "blocked-unsafe", None
    if not records:
        return "create", None
    record = records[0]
    if record.get("state") != "OPEN" or not provenance_matches(record, provenance, issue) or not pull_request_identity_matches(repository, record, base, branch):
        return "blocked-unsafe", record
    return "reuse", record


def parse_remote_head(stdout: str, branch: str) -> tuple[str | None, bool]:
    lines = [line.split() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None, True
    if len(lines) != 1 or len(lines[0]) != 2 or lines[0][1] != f"refs/heads/{branch}":
        return None, False
    return lines[0][0], True


def classify_push_failure(stderr: str) -> tuple[str, str]:
    lowered = stderr.lower()
    unsafe_markers = ("non-fast-forward", "fetch first", "stale info", "would clobber")
    if any(marker in lowered for marker in unsafe_markers):
        return "blocked", "blocked-unsafe"
    return "waiting", "waiting-external"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--provenance", choices=("cli", "openchamber", "github-issue"), required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--validated-head", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--issue")
    parser.add_argument("--base", default="main")
    args = parser.parse_args()

    evidence: dict[str, object] = {"provenance": args.provenance}
    if (args.provenance == "github-issue") != bool(args.issue):
        return result("blocked", "blocked-unsafe", evidence, "issue identity must be supplied only for github-issue provenance")
    if args.issue and not args.issue.lstrip("#").isdigit():
        return result("blocked", "blocked-unsafe", evidence, "issue identity must be a numeric issue number")
    if args.validated_head != args.expected_head:
        return result("blocked", "blocked-unsafe", evidence, "validated head does not match the expected publication head")
    if has_reserved_markers(args.body):
        return result("blocked", "blocked-unsafe", evidence, "caller-provided body contains reserved lifecycle markers")

    for command in (["gh", "auth", "status"], ["gh", "repo", "view", "--json", "nameWithOwner,url"]):
        completed = run(command)
        if completed.returncode != 0:
            return result("waiting", "waiting-external", evidence, completed.stderr.strip())
        if command[1:3] == ["repo", "view"]:
            try:
                repository = json.loads(completed.stdout)
            except json.JSONDecodeError as exc:
                return result("blocked", "blocked-unsafe", evidence, f"invalid repository JSON: {exc}")
            if not isinstance(repository, dict) or not repository.get("nameWithOwner") or not repository.get("url"):
                return result("blocked", "blocked-unsafe", evidence, "repository identity is incomplete")
            evidence["repository"] = repository

    origin = run(["git", "remote", "get-url", "--all", "origin"])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", "origin"])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return result("blocked", "blocked-unsafe", evidence, "origin remote identity is unavailable")
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return result("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository")

    branch_result = run(["git", "branch", "--show-current"])
    head_result = run(["git", "rev-parse", "HEAD"])
    status_result = run(["git", "status", "--porcelain=v1"])
    if any(command.returncode != 0 for command in (branch_result, head_result, status_result)):
        return result("blocked", "blocked-unsafe", evidence, "cannot resolve current Git state")
    branch = branch_result.stdout.strip()
    head = head_result.stdout.strip()
    evidence.update({"branch": branch, "head": head, "clean": status_result.stdout == ""})
    if not branch or branch == args.base or head != args.expected_head or status_result.stdout:
        return result("blocked", "blocked-unsafe", evidence, "branch, head, or clean-state invariant failed")

    owner_repo = repository["nameWithOwner"]
    fields = "number,state,url,title,body,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"
    listed = run(["gh", "pr", "list", "--repo", owner_repo, "--head", branch, "--state", "all", "--json", fields])
    if listed.returncode != 0:
        return result("waiting", "waiting-external", evidence, listed.stderr.strip())
    try:
        records = json.loads(listed.stdout)
    except json.JSONDecodeError as exc:
        return result("blocked", "blocked-unsafe", evidence, f"invalid pull-request JSON: {exc}")
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        return result("blocked", "blocked-unsafe", evidence, "pull-request list shape is invalid")
    action, record = select_pull_request(records, repository, args.provenance, args.issue, args.base, branch)
    if action == "blocked-unsafe":
        evidence["pull_requests"] = records
        return result("blocked", action, evidence, "branch has multiple or non-open pull requests")

    refspec = f"{args.expected_head}:refs/heads/{branch}"
    pushed = run(["git", "push", "--set-upstream", "origin", refspec])
    if pushed.returncode != 0:
        status, disposition = classify_push_failure(pushed.stderr)
        return result(status, disposition, evidence, pushed.stderr.strip())
    post_branch = run(["git", "branch", "--show-current"])
    post_head = run(["git", "rev-parse", "HEAD"])
    post_status = run(["git", "status", "--porcelain=v1"])
    if any(command.returncode != 0 for command in (post_branch, post_head, post_status)) or post_branch.stdout.strip() != branch or post_head.stdout.strip() != args.expected_head or post_status.stdout:
        return result("blocked", "blocked-unsafe", evidence, "local branch, head, or clean state changed during publication")
    remote = run(["git", "ls-remote", "--heads", "origin", branch])
    if remote.returncode != 0:
        return result("waiting", "waiting-external", evidence, remote.stderr.strip())
    remote_head, remote_valid = parse_remote_head(remote.stdout, branch)
    evidence["remote_head"] = remote_head
    if not remote_valid or remote_head != args.expected_head:
        return result("blocked", "blocked-unsafe", evidence, "remote branch does not match the validated publication head")

    if action == "create":
        body = canonical_body(args.provenance, args.body, args.issue)
        created = run([
            "gh", "pr", "create", "--repo", owner_repo, "--draft", "--base", args.base, "--head", branch,
            "--title", args.title, "--body-file", "-",
        ], input_text=body)
        if created.returncode != 0:
            evidence["remote_branch_without_pr"] = True
            return result("waiting", "waiting-external", evidence, created.stderr.strip(), "pr-publication")
        evidence["created_output"] = created.stdout.strip()

    verified = run(["gh", "pr", "list", "--repo", owner_repo, "--head", branch, "--state", "open", "--json", fields])
    if verified.returncode != 0:
        return result("waiting", "waiting-external", evidence, verified.stderr.strip())
    try:
        open_records = json.loads(verified.stdout)
    except json.JSONDecodeError as exc:
        return result("blocked", "blocked-unsafe", evidence, f"invalid verification JSON: {exc}")
    if (
        not isinstance(open_records, list)
        or len(open_records) != 1
        or not isinstance(open_records[0], dict)
        or not pull_request_identity_matches(repository, open_records[0], args.base, branch)
        or not provenance_matches(open_records[0], args.provenance, args.issue)
    ):
        evidence["verification"] = open_records
        return result("blocked", "blocked-unsafe", evidence, "published pull request does not match expected head and base")
    if open_records[0].get("headRefOid") != head:
        evidence["verification"] = open_records
        return result("waiting", "waiting-external", evidence, "GitHub has not yet exposed the pushed head", "pr-publication")
    evidence["pull_request"] = open_records[0]
    disposition = "created" if action == "create" else "updated" if record and record.get("headRefOid") != head else "reused"
    return result("passed", disposition, evidence, None, "hosted-checks")


if __name__ == "__main__":
    sys.exit(main())
