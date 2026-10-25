#!/usr/bin/env python3
"""Classify required GitHub checks without LLM interpretation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from urllib.parse import urlparse


VERSION = 1
PASSING = {("pass", "SUCCESS"), ("pass", "NEUTRAL")}
PENDING = {("pending", "QUEUED"), ("pending", "PENDING"), ("pending", "IN_PROGRESS"), ("pending", "WAITING")}
FAILED = {
    ("fail", "FAILURE"), ("fail", "ERROR"), ("fail", "TIMED_OUT"),
    ("fail", "ACTION_REQUIRED"), ("cancel", "CANCELLED"),
    ("skipping", "SKIPPED"), ("skipping", "STALE"),
}


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, text=True, capture_output=True, check=False)


def classify(exit_code: int, stdout: str, stderr: str) -> tuple[str, list[dict] | None]:
    if stdout:
        try:
            records = json.loads(stdout)
        except json.JSONDecodeError:
            return "blocked-unsafe", None
        if not isinstance(records, list):
            return "blocked-unsafe", None
        if not records:
            return "zero-candidate" if exit_code == 0 and not stderr else "blocked-unsafe", records
        kinds: list[str] = []
        for record in records:
            if not isinstance(record, dict) or not record.get("name"):
                return "blocked-unsafe", records
            pair = (record.get("bucket"), record.get("state"))
            if pair in PASSING:
                kinds.append("pass")
            elif pair in PENDING:
                kinds.append("pending")
            elif pair in FAILED:
                kinds.append("fail")
            else:
                return "blocked-unsafe", records
        if exit_code == 0 and all(kind == "pass" for kind in kinds):
            return "passed", records
        if exit_code == 8 and "pending" in kinds and all(kind in ("pass", "pending") for kind in kinds):
            return "pending", records
        if exit_code == 1 and "fail" in kinds:
            return "repair-needed", records
        return "blocked-unsafe", records
    if exit_code == 1 and stderr.startswith("no required checks reported on the '") and stderr.rstrip().endswith("' branch"):
        return "zero-candidate", []
    return "blocked-unsafe", None


def emit(status: str, disposition: str, evidence: dict, blocker: str | None = None) -> int:
    print(json.dumps({
        "version": VERSION,
        "status": status,
        "disposition": disposition,
        "next_stage": "pull-request-ready" if disposition == "passed" else "correction" if disposition == "repair-needed" else None,
        "evidence": evidence,
        "blocker": blocker,
    }, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else 4 if status == "repair" else 2


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


def verify_zero(owner_repo: str, base: str) -> tuple[bool, dict]:
    protection = run(["gh", "api", "--include", f"repos/{owner_repo}/branches/{base}/protection"])
    rulesets = run(["gh", "api", f"repos/{owner_repo}/rulesets?includes_parents=true"])
    evidence = {"protection_stdout": protection.stdout, "protection_stderr": protection.stderr, "rulesets_stdout": rulesets.stdout, "rulesets_stderr": rulesets.stderr}
    protection_status_ok = "HTTP/2.0 404" in protection.stdout or "HTTP/1.1 404" in protection.stdout
    protection_body = protection.stdout[protection.stdout.rfind("{"):] if "{" in protection.stdout else ""
    try:
        protection_json = json.loads(protection_body)
    except json.JSONDecodeError:
        protection_json = None
    try:
        rulesets_json = json.loads(rulesets.stdout)
    except json.JSONDecodeError:
        rulesets_json = None
    protection_ok = protection_status_ok and isinstance(protection_json, dict) and protection_json.get("message") == "Branch not protected"
    return protection_ok and rulesets.returncode == 0 and rulesets_json == [], evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", required=True)
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--max-rechecks", type=int, default=5)
    parser.add_argument("--wait-seconds", type=int, default=30)
    args = parser.parse_args()
    evidence: dict[str, object] = {"attempts": []}
    if args.max_rechecks < 0 or args.wait_seconds < 0:
        return emit("blocked", "blocked-unsafe", evidence, "recheck count and wait interval must be nonnegative")

    auth = run(["gh", "auth", "status"])
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    if auth.returncode != 0 or repo.returncode != 0:
        return emit("waiting", "waiting-external", evidence, (auth.stderr or repo.stderr).strip())
    try:
        repository = json.loads(repo.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", evidence, "invalid repository JSON")
    if not isinstance(repository, dict) or not repository.get("nameWithOwner") or not repository.get("url"):
        return emit("blocked", "blocked-unsafe", evidence, "repository identity is incomplete")
    evidence["repository"] = repository

    origin = run(["git", "remote", "get-url", "--all", "origin"])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", "origin"])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return emit("blocked", "blocked-unsafe", evidence, "origin remote identity is unavailable")
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return emit("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository")

    identity_fields = "number,url,state,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"
    initial = run(["gh", "pr", "view", args.pr, "--json", identity_fields])
    if initial.returncode != 0:
        return emit("waiting", "waiting-external", evidence, initial.stderr.strip())
    try:
        identity = json.loads(initial.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", evidence, "invalid pull-request JSON")
    required_identity = ("number", "url", "baseRefName", "headRefName", "headRefOid")
    if not isinstance(identity, dict) or identity.get("state") != "OPEN" or identity.get("headRefOid") != args.expected_head or any(not identity.get(key) for key in required_identity):
        return emit("blocked", "blocked-unsafe", evidence, "pull request is not open at the expected head")
    if not repository_matches(repository, identity):
        return emit("blocked", "blocked-unsafe", evidence, "pull request does not belong to the current repository")
    if not head_repository_matches(repository, identity):
        return emit("blocked", "blocked-unsafe", evidence, "pull request head repository does not match origin")
    evidence["pull_request"] = identity
    pr_number = str(identity["number"])
    owner_repo = repository["nameWithOwner"]

    for attempt in range(args.max_rechecks + 1):
        checked = run(["gh", "pr", "checks", pr_number, "--repo", owner_repo, "--required", "--json", "bucket,name,state,workflow,link"])
        disposition, records = classify(checked.returncode, checked.stdout, checked.stderr)
        evidence["attempts"].append({"attempt": attempt + 1, "exit_code": checked.returncode, "stdout": checked.stdout, "stderr": checked.stderr, "classification": disposition, "records": records})
        current = run(["gh", "pr", "view", pr_number, "--repo", owner_repo, "--json", identity_fields])
        if current.returncode != 0:
            return emit("waiting", "waiting-external", evidence, current.stderr.strip())
        try:
            current_identity = json.loads(current.stdout)
        except json.JSONDecodeError:
            return emit("blocked", "blocked-unsafe", evidence, "invalid pull-request recheck JSON")
        if current_identity != identity:
            return emit("blocked", "blocked-unsafe", evidence, "pull-request identity or head changed during check validation")
        if disposition == "passed":
            return emit("passed", "passed", evidence)
        if disposition == "repair-needed":
            return emit("repair", "repair-needed", evidence, "one or more required checks failed")
        if disposition == "blocked-unsafe":
            return emit("blocked", disposition, evidence, "required-check output was malformed or ambiguous")
        if disposition == "zero-candidate":
            expected_empty_error = f"no required checks reported on the '{identity['headRefName']}' branch"
            if not checked.stdout and checked.stderr.rstrip() != expected_empty_error:
                return emit("blocked", "blocked-unsafe", evidence, "empty required-check output named an unexpected branch")
            zero_ok, zero_evidence = verify_zero(repository["nameWithOwner"], identity["baseRefName"])
            evidence["zero_configuration"] = zero_evidence
            return emit("passed", "passed", evidence) if zero_ok else emit("blocked", "blocked-unsafe", evidence, "zero required-check configuration is ambiguous")
        if attempt < args.max_rechecks:
            time.sleep(args.wait_seconds)
    return emit("waiting", "waiting-external", evidence, "required checks remain pending after the bounded recheck window")


if __name__ == "__main__":
    sys.exit(main())
