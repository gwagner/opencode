#!/usr/bin/env python3
"""Classify required GitHub checks without LLM interpretation."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time


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
    evidence["repository"] = repository

    initial = run(["gh", "pr", "view", args.pr, "--json", "number,url,state,baseRefName,headRefName,headRefOid"])
    if initial.returncode != 0:
        return emit("waiting", "waiting-external", evidence, initial.stderr.strip())
    try:
        identity = json.loads(initial.stdout)
    except json.JSONDecodeError:
        return emit("blocked", "blocked-unsafe", evidence, "invalid pull-request JSON")
    required_identity = ("number", "url", "baseRefName", "headRefName", "headRefOid")
    if identity.get("state") != "OPEN" or identity.get("headRefOid") != args.expected_head or any(not identity.get(key) for key in required_identity):
        return emit("blocked", "blocked-unsafe", evidence, "pull request is not open at the expected head")
    evidence["pull_request"] = identity

    for attempt in range(args.max_rechecks + 1):
        checked = run(["gh", "pr", "checks", args.pr, "--required", "--json", "bucket,name,state,workflow,link"])
        disposition, records = classify(checked.returncode, checked.stdout, checked.stderr)
        evidence["attempts"].append({"attempt": attempt + 1, "exit_code": checked.returncode, "stdout": checked.stdout, "stderr": checked.stderr, "classification": disposition, "records": records})
        current = run(["gh", "pr", "view", args.pr, "--json", "number,url,state,baseRefName,headRefName,headRefOid"])
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
