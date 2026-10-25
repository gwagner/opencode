#!/usr/bin/env python3
"""Classify required GitHub checks without LLM interpretation."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_policy_argument, load_policy, policy_evidence
from github_pr_lifecycle_common import (
    emit as result_emit,
    head_repository_matches,
    remote_urls_match,
    repository_matches,
    run,
)
PASSING = {("pass", "SUCCESS"), ("pass", "NEUTRAL")}
PENDING = {("pending", "QUEUED"), ("pending", "PENDING"), ("pending", "IN_PROGRESS"), ("pending", "WAITING")}
FAILED = {
    ("fail", "FAILURE"), ("fail", "ERROR"), ("fail", "TIMED_OUT"),
    ("fail", "ACTION_REQUIRED"), ("cancel", "CANCELLED"),
    ("skipping", "SKIPPED"), ("skipping", "STALE"),
}



def classify(exit_code: int, stdout: str, stderr: str) -> tuple[str, list[dict] | None]:
    if stdout:
        try:
            records = json.loads(stdout)
        except json.JSONDecodeError:
            return ("blocked-unsafe" if exit_code == 0 else "waiting-external"), None
        if not isinstance(records, list):
            return ("blocked-unsafe" if exit_code == 0 else "waiting-external"), None
        if not records:
            return "zero-candidate" if exit_code == 0 and not stderr else "blocked-unsafe", records
        kinds: list[str] = []
        for record in records:
            if not isinstance(record, dict) or not record.get("name"):
                return ("blocked-unsafe" if exit_code == 0 else "waiting-external"), records
            pair = (record.get("bucket"), record.get("state"))
            if pair in PASSING:
                kinds.append("pass")
            elif pair in PENDING:
                kinds.append("pending")
            elif pair in FAILED:
                kinds.append("fail")
            else:
                return ("blocked-unsafe" if exit_code == 0 else "waiting-external"), records
        if exit_code == 0 and all(kind == "pass" for kind in kinds):
            return "passed", records
        if exit_code == 8 and "pending" in kinds and all(kind in ("pass", "pending") for kind in kinds):
            return "pending", records
        if exit_code == 1 and "fail" in kinds:
            return "repair-needed", records
        return ("blocked-unsafe" if exit_code == 0 else "waiting-external"), records
    if exit_code == 1 and stderr.startswith("no required checks reported on the '") and stderr.rstrip().endswith("' branch"):
        return "zero-candidate", []
    return ("blocked-unsafe" if exit_code == 0 else "waiting-external"), None



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
    parser.add_argument("--max-rechecks", type=int, default=None)
    parser.add_argument("--wait-seconds", type=int, default=30)
    add_policy_argument(parser)
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy, args.expected_policy_digest)
    except ValueError as exc:
        return result_emit("blocked", "blocked-unsafe", {}, str(exc))
    evidence: dict[str, object] = {**policy_evidence(policy), "attempts": []}
    args.max_rechecks = policy["validation"]["max_rechecks"] if args.max_rechecks is None else args.max_rechecks
    args.wait_seconds = policy["validation"]["wait_seconds"] if args.wait_seconds == 30 else args.wait_seconds
    if args.max_rechecks < 0 or args.wait_seconds < 0:
        return result_emit("blocked", "blocked-unsafe", evidence, "recheck count and wait interval must be nonnegative")

    auth = run(["gh", "auth", "status"])
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    if auth.returncode != 0 or repo.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, (auth.stderr or repo.stderr).strip())
    try:
        repository = json.loads(repo.stdout)
    except json.JSONDecodeError:
        return result_emit("blocked", "blocked-unsafe", evidence, "invalid repository JSON")
    if not isinstance(repository, dict) or not repository.get("nameWithOwner") or not repository.get("url"):
        return result_emit("blocked", "blocked-unsafe", evidence, "repository identity is incomplete")
    evidence["repository"] = repository

    origin = run(["git", "remote", "get-url", "--all", policy["remote"]])
    push_origin = run(["git", "remote", "get-url", "--push", "--all", policy["remote"]])
    if origin.returncode != 0 or push_origin.returncode != 0:
        return result_emit("blocked", "blocked-unsafe", evidence, "origin remote identity is unavailable")
    evidence["origin_url"] = origin.stdout.strip()
    evidence["origin_push_url"] = push_origin.stdout.strip()
    if not remote_urls_match(repository, origin.stdout) or not remote_urls_match(repository, push_origin.stdout):
        return result_emit("blocked", "blocked-unsafe", evidence, "origin does not match the verified GitHub repository")

    identity_fields = "number,url,state,baseRefName,headRefName,headRefOid,isCrossRepository,headRepository"
    initial = run(["gh", "pr", "view", args.pr, "--repo", repository["nameWithOwner"], "--json", identity_fields])
    if initial.returncode != 0:
        return result_emit("waiting", "waiting-external", evidence, initial.stderr.strip())
    try:
        identity = json.loads(initial.stdout)
    except json.JSONDecodeError:
        return result_emit("blocked", "blocked-unsafe", evidence, "invalid pull-request JSON")
    required_identity = ("number", "url", "baseRefName", "headRefName", "headRefOid")
    if not isinstance(identity, dict) or identity.get("state") != "OPEN" or identity.get("headRefOid") != args.expected_head or any(not identity.get(key) for key in required_identity):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request is not open at the expected head")
    if identity.get("baseRefName") != policy["base_branch"]:
        return result_emit("blocked", "blocked-unsafe", evidence, "check validation base must equal the lifecycle policy base")
    if not repository_matches(repository, identity):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request does not belong to the current repository")
    if not head_repository_matches(repository, identity):
        return result_emit("blocked", "blocked-unsafe", evidence, "pull request head repository does not match origin")
    evidence["pull_request"] = identity
    pr_number = str(identity["number"])
    owner_repo = repository["nameWithOwner"]

    for attempt in range(args.max_rechecks + 1):
        command = ["gh", "pr", "checks", pr_number, "--repo", owner_repo]
        if policy["validation"]["check_mode"] == "required":
            command.append("--required")
        command.extend(["--json", "bucket,name,state,workflow,link"])
        checked = run(command)
        disposition, records = classify(checked.returncode, checked.stdout, checked.stderr)
        allowed_checks = policy["validation"]["check_names"]
        if allowed_checks and records is not None:
            names = [record.get("name") for record in records]
            if sorted(names) != sorted(allowed_checks) or len(names) != len(set(names)):
                return result_emit("blocked", "blocked-unsafe", evidence, "check names must match the policy exactly once")
        evidence["attempts"].append({"attempt": attempt + 1, "exit_code": checked.returncode, "stdout": checked.stdout, "stderr": checked.stderr, "classification": disposition, "records": records})
        current = run(["gh", "pr", "view", pr_number, "--repo", owner_repo, "--json", identity_fields])
        if current.returncode != 0:
            return result_emit("waiting", "waiting-external", evidence, current.stderr.strip())
        try:
            current_identity = json.loads(current.stdout)
        except json.JSONDecodeError:
            return result_emit("blocked", "blocked-unsafe", evidence, "invalid pull-request recheck JSON")
        if current_identity != identity:
            return result_emit("blocked", "blocked-unsafe", evidence, "pull-request identity or head changed during check validation")
        if disposition == "passed":
            return result_emit("passed", "passed", evidence, next_stage="pull-request-ready")
        if disposition == "repair-needed":
            return result_emit("repair", "repair-needed", evidence, "one or more required checks failed", "correction")
        if disposition == "blocked-unsafe":
            return result_emit("blocked", disposition, evidence, "required-check output was malformed or ambiguous")
        if disposition == "waiting-external":
            return result_emit("waiting", disposition, evidence, checked.stderr.strip() or "required-check transport failed")
        if disposition == "zero-candidate":
            expected_empty_error = f"no required checks reported on the '{identity['headRefName']}' branch"
            if not checked.stdout and checked.stderr.rstrip() != expected_empty_error:
                return result_emit("blocked", "blocked-unsafe", evidence, "empty required-check output named an unexpected branch")
            zero_ok, zero_evidence = verify_zero(repository["nameWithOwner"], identity["baseRefName"])
            evidence["zero_configuration"] = zero_evidence
            return result_emit("passed", "passed", evidence, next_stage="pull-request-ready") if zero_ok else result_emit("blocked", "blocked-unsafe", evidence, "zero required-check configuration is ambiguous")
        if attempt < args.max_rechecks:
            time.sleep(args.wait_seconds)
    return result_emit("waiting", "waiting-external", evidence, "required checks remain pending after the bounded recheck window")


if __name__ == "__main__":
    sys.exit(main())
