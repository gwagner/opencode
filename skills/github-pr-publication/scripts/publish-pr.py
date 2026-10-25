#!/usr/bin/env python3
"""Idempotently push the current head and create or update one draft PR."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys


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


def provenance_matches(record: dict, provenance: str, issue: str | None) -> bool:
    lines = (record.get("body") or "").splitlines()
    if f"OpenCode-Origin: {provenance}" not in lines:
        return False
    return provenance != "github-issue" or f"Refs #{issue.lstrip('#') if issue else ''}" in lines


def select_pull_request(records: list[dict], provenance: str, issue: str | None) -> tuple[str, dict | None]:
    if len(records) > 1:
        return "blocked-unsafe", None
    if not records:
        return "create", None
    record = records[0]
    if record.get("state") != "OPEN" or not provenance_matches(record, provenance, issue):
        return "blocked-unsafe", record
    return "reuse", record


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

    listed = run(["gh", "pr", "list", "--head", branch, "--state", "all", "--json", "number,state,url,title,body,baseRefName,headRefName,headRefOid"])
    if listed.returncode != 0:
        return result("waiting", "waiting-external", evidence, listed.stderr.strip())
    try:
        records = json.loads(listed.stdout)
    except json.JSONDecodeError as exc:
        return result("blocked", "blocked-unsafe", evidence, f"invalid pull-request JSON: {exc}")
    action, record = select_pull_request(records, args.provenance, args.issue)
    if action == "blocked-unsafe":
        evidence["pull_requests"] = records
        return result("blocked", action, evidence, "branch has multiple or non-open pull requests")

    pushed = run(["git", "push", "--set-upstream", "origin", branch])
    if pushed.returncode != 0:
        status, disposition = classify_push_failure(pushed.stderr)
        return result(status, disposition, evidence, pushed.stderr.strip())

    if action == "create":
        body = canonical_body(args.provenance, args.body, args.issue)
        created = run([
            "gh", "pr", "create", "--draft", "--base", args.base, "--head", branch,
            "--title", args.title, "--body-file", "-",
        ], input_text=body)
        if created.returncode != 0:
            evidence["remote_branch_without_pr"] = True
            return result("waiting", "waiting-external", evidence, created.stderr.strip(), "pr-publication")
        evidence["created_output"] = created.stdout.strip()

    verified = run(["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number,state,url,title,body,baseRefName,headRefName,headRefOid"])
    if verified.returncode != 0:
        return result("waiting", "waiting-external", evidence, verified.stderr.strip())
    try:
        open_records = json.loads(verified.stdout)
    except json.JSONDecodeError as exc:
        return result("blocked", "blocked-unsafe", evidence, f"invalid verification JSON: {exc}")
    if (
        len(open_records) != 1
        or open_records[0].get("baseRefName") != args.base
        or open_records[0].get("headRefName") != branch
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
