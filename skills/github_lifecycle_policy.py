"""Fail-closed, versioned policy used by GitHub lifecycle scripts."""
from __future__ import annotations

import copy
import json
from pathlib import Path

DEFAULT_POLICY = {
    "version": 1,
    "base_branch": "main",
    "feature_branch_prefix": "feature/",
    "provenance": ["cli", "openchamber", "github-issue"],
    "remote": "origin",
    "authorization": {
        "commit": False,
        "publication": False,
        "cleanup": False,
        "comment": False,
        "closure": False,
        "ready": False,
        "rejection": False,
    },
    "evidence": {
        "current_id": "current",
        "completion_id": "merged-pr",
        "require_authenticated_actor": True,
        "actor_transfer": "immutable-author-derived",
    },
    "manual_merge": {"method": "squash", "require_current_turn_attestation": True},
    "pull_request": {"ready_policy": "auto", "rejection_policy": "leave-open"},
    "recovery": {"require_exact_head": True, "disambiguation": "block", "selector": "exact-pr-url-or-number"},
    "validation": {"check_mode": "required", "check_names": [], "max_rechecks": 5, "wait_seconds": 30, "max_corrections": 1, "visual_scenarios": []},
    "delegates": {"hints": [], "commit_strategy": "sequential-reviewed", "message_scope": "per-batch"},
    "remote_cleanup": "delete",
    "issue_completion": "close",
    "blocked_issue_creation": False,
}

def add_policy_argument(parser) -> None:
    parser.add_argument("--policy", help="optional JSON lifecycle policy override")

def add_authorization_argument(parser, action: str) -> None:
    parser.add_argument(f"--authorize-{action}", action="store_true", help=f"explicit authorization for {action}")

def authorized(policy: dict, action: str, supplied: bool) -> bool:
    """Explicit caller authorization is required unless policy grants the action."""
    return supplied or policy["authorization"][action] is True

def load_policy(path: str | None) -> dict:
    policy = copy.deepcopy(DEFAULT_POLICY)
    if path:
        try:
            supplied = json.loads(Path(path).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid lifecycle policy: {exc}") from exc
        if not isinstance(supplied, dict):
            raise ValueError("lifecycle policy must be a JSON object")
        _merge(policy, supplied, "")
    _validate(policy)
    return policy

def _merge(target: dict, source: dict, path: str) -> None:
    for key, value in source.items():
        if key not in target:
            raise ValueError(f"unsupported lifecycle policy key: {path}{key}")
        if isinstance(target[key], dict):
            if not isinstance(value, dict):
                raise ValueError(f"lifecycle policy object required: {path}{key}")
            _merge(target[key], value, f"{path}{key}.")
        elif type(value) is not type(target[key]):
            raise ValueError(f"invalid lifecycle policy type: {path}{key}")
        else:
            target[key] = value

def _validate(policy: dict) -> None:
    if policy["version"] != 1:
        raise ValueError("unsupported lifecycle policy version")
    if not all(isinstance(policy[k], str) and policy[k] for k in ("base_branch", "feature_branch_prefix", "remote")) or not policy["feature_branch_prefix"].endswith("/"):
        raise ValueError("base_branch, remote, and slash-terminated feature_branch_prefix are required")
    if not policy["provenance"] or any(x not in DEFAULT_POLICY["provenance"] for x in policy["provenance"]):
        raise ValueError("provenance must be a nonempty supported subset")
    if any(type(v) is not bool for v in policy["authorization"].values()):
        raise ValueError("authorization values must be booleans")
    if policy["manual_merge"]["method"] not in ("squash", "merge", "rebase") or type(policy["manual_merge"]["require_current_turn_attestation"]) is not bool:
        raise ValueError("manual_merge method or attestation is invalid")
    if policy["pull_request"]["ready_policy"] not in ("auto", "ask", "keep-draft") or policy["pull_request"]["rejection_policy"] not in ("leave-open", "close-pr"):
        raise ValueError("pull-request policy is invalid")
    if policy["recovery"]["disambiguation"] != "block" or policy["recovery"]["selector"] != "exact-pr-url-or-number" or type(policy["recovery"]["require_exact_head"]) is not bool:
        raise ValueError("recovery policy is invalid")
    v = policy["validation"]
    if v["check_mode"] not in ("required", "all") or any(not isinstance(x, str) or not x for x in v["check_names"] + v["visual_scenarios"]) or any(type(v[k]) is not int or v[k] < 0 for k in ("max_rechecks", "wait_seconds", "max_corrections")):
        raise ValueError("validation policy is invalid")
    if policy["delegates"]["commit_strategy"] not in ("sequential-reviewed", "single-task") or policy["delegates"]["message_scope"] not in ("per-batch", "single-task") or any(not isinstance(x, str) or not x for x in policy["delegates"]["hints"]):
        raise ValueError("delegate policy is invalid")
    if policy["remote_cleanup"] not in ("delete", "retain") or policy["issue_completion"] not in ("close", "comment-only", "none"):
        raise ValueError("completion policy is invalid")
    if policy["issue_completion"] == "close" and policy["remote_cleanup"] != "delete":
        raise ValueError("issue_completion close requires remote_cleanup delete")
    if type(policy["blocked_issue_creation"]) is not bool or policy["evidence"]["actor_transfer"] != "immutable-author-derived" or policy["evidence"]["require_authenticated_actor"] is not True:
        raise ValueError("immutable authenticated actor evidence is required")

def policy_evidence(policy: dict) -> dict:
    return {"policy": policy}
