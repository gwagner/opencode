#!/usr/bin/env python3
"""Close one issue only after authoritative, current recovery verification."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_authorization_argument, add_policy_argument, authorized, load_policy, policy_digest, policy_evidence
from github_pr_lifecycle_common import emit, run


def recovery_command(args, policy_path: str) -> list[str]:
    command = [
        "python3",
        "/code/skills/github-sdlc-lifecycle-recovery/scripts/recover-lifecycle.py",
        "--issue", args.issue,
        "--completion-pr", args.expected_pr,
        "--completion-head", args.expected_head,
        "--completion-branch", args.expected_branch,
        "--completion-merge-commit", args.expected_merge_commit,
    ]
    command.extend(["--policy", policy_path, "--expected-policy-digest", args.expected_policy_digest, "--repository", args.repository, "--lifecycle-run", args.lifecycle_run])
    return command


def recover(args, policy_path: str) -> tuple[dict | None, str | None]:
    completed = run(recovery_command(args, policy_path))
    # Lifecycle envelopes are meaningful even when their status maps to a
    # nonzero process exit.  Parse stdout directly so a safe waiting/blocker is
    # preserved instead of being mislabeled as malformed recovery.
    try:
        import json
        result = json.loads(completed.stdout)
    except json.JSONDecodeError:
        result = None
    if result is None or result.get("version") != 1:
        return None, "recovery result is malformed"
    if result.get("status") != "passed":
        return None, result.get("blocker") or "recovery did not establish closure safety"
    return result, None


def unchanged_policy(path: str, expected_digest: str, repository: str, lifecycle_run: str) -> bool:
    try:
        return policy_digest(path, repository, lifecycle_run) == expected_digest
    except OSError:
        return False

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--issue", required=True)
    p.add_argument("--expected-pr", required=True)
    p.add_argument("--expected-head", required=True)
    p.add_argument("--expected-branch", required=True)
    p.add_argument("--expected-merge-commit", required=True)
    add_policy_argument(p); add_authorization_argument(p, "closure"); a=p.parse_args()
    try: policy=load_policy(a.policy, a.expected_policy_digest, a.repository, a.lifecycle_run)
    except ValueError as e: return emit("blocked", "blocked-unsafe", {}, str(e))
    evidence = policy_evidence(policy)
    try:
        expected_policy_digest = policy_digest(a.policy, a.repository, a.lifecycle_run)
    except OSError as exc:
        return emit("blocked", "blocked-unsafe", evidence, f"policy snapshot is unavailable: {exc}")
    evidence["policy_digest"] = expected_policy_digest
    if policy["issue_completion"] != "close":
        return emit("passed", "retained", evidence, next_stage="completion")
    if not authorized(policy, "closure", a.authorize_closure):
        return emit("waiting", "waiting-user-authorization", evidence, "current-turn closure authorization is required")
    before, blocker = recover(a, a.policy)
    if before is None:
        return emit("blocked", "blocked-unsafe", evidence, blocker)
    evidence["recovery_before"] = before
    if not unchanged_policy(a.policy, expected_policy_digest, a.repository, a.lifecycle_run):
        return emit("blocked", "blocked-unsafe", evidence, "policy source changed after recovery")
    if before.get("disposition") == "closed":
        return emit("passed", "already-closed", evidence)
    if before.get("disposition") != "merged-needs-close":
        return emit("blocked", "blocked-unsafe", evidence, "recovery does not permit closure")
    repository = ((before.get("evidence") or {}).get("repository"))
    if not isinstance(repository, dict) or not isinstance(repository.get("nameWithOwner"), str) or not repository["nameWithOwner"]:
        return emit("blocked", "blocked-unsafe", evidence, "recovery repository binding is malformed")
    closed = run(["gh", "issue", "close", a.issue, "--repo", repository["nameWithOwner"]])
    evidence["close_exit_code"] = closed.returncode
    if closed.returncode != 0:
        return emit("waiting", "waiting-external", evidence, closed.stderr.strip() or "issue close was not confirmed")
    after, blocker = recover(a, a.policy)
    if after is None or after.get("disposition") != "closed":
        return emit("blocked", "blocked-unsafe", evidence, blocker or "post-close recovery did not prove closure")
    evidence["recovery_after"] = after
    if not unchanged_policy(a.policy, expected_policy_digest, a.repository, a.lifecycle_run):
        return emit("blocked", "blocked-unsafe", evidence, "policy source changed during closure")
    return emit("passed", "closed", evidence)
if __name__ == "__main__": raise SystemExit(main())
