"""Fail-closed, versioned policy used by GitHub lifecycle scripts."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path

DEFAULT_POLICY = {
    "version": 1,
    "base_branch": "main",
    "feature_branch_prefix": "feature/",
    "provenance": ["cli", "openchamber", "github-issue"],
    "remote": "origin",
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
    "remote_cleanup": "delete",
    "issue_completion": "close",
    "blocked_issue_creation": False,
}
SNAPSHOT_PATH = "/tmp/opencode/lifecycle-policy.snapshot.json"

def add_policy_argument(parser) -> None:
    parser.add_argument("--policy", required=True, help="fixed immutable lifecycle policy snapshot")
    parser.add_argument("--expected-policy-digest", required=True, help="SHA-256 of the immutable resolved policy snapshot")

def add_authorization_argument(parser, action: str) -> None:
    parser.add_argument(f"--authorize-{action}", action="store_true", help=f"explicit authorization for {action}")

def authorized(policy: dict, action: str, supplied: bool) -> bool:
    """A mutating operation needs an authorization flag from this invocation.

    Policy is an immutable configuration input, not a durable grant of authority.
    Keep ``policy`` and ``action`` in this interface so every lifecycle operation
    uses the same explicit gate and callers cannot select an alternate gate.
    """
    del policy, action
    return supplied is True

def load_policy(path: str | None, expected_digest: str | None = None) -> dict:
    """Load only the fixed resolver-produced snapshot bound to its exact bytes."""
    if path != SNAPSHOT_PATH:
        raise ValueError("policy path must be the fixed lifecycle policy snapshot")
    if not expected_digest or not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
        raise ValueError("expected lifecycle policy snapshot digest is required")
    try:
        source = Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f"invalid lifecycle policy: {exc}") from exc
    digest = hashlib.sha256(source).hexdigest()
    if digest != expected_digest:
        raise ValueError("policy snapshot digest does not match the expected digest")
    return _load_normalized_policy(source, digest)


def resolve_policy_source(source: bytes | None) -> tuple[dict, bytes, str]:
    """Validate and normalize the resolver's optional caller-provided source."""
    policy = copy.deepcopy(DEFAULT_POLICY)
    if source is not None:
        try:
            supplied = json.loads(source)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid lifecycle policy: {exc}") from exc
        if not isinstance(supplied, dict):
            raise ValueError("lifecycle policy must be a JSON object")
        _merge(policy, supplied, "")
    _validate(policy)
    normalized = json.dumps(policy, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    digest = hashlib.sha256(normalized).hexdigest()
    policy["_snapshot_digest"] = digest
    return policy, normalized, digest


def _load_normalized_policy(source: bytes, digest: str) -> dict:
    policy, normalized, normalized_digest = resolve_policy_source(source)
    if source != normalized or digest != normalized_digest:
        raise ValueError("lifecycle policy snapshot is not normalized")
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
    if not _git_ref(policy["base_branch"]) or not _git_ref(policy["feature_branch_prefix"][:-1]) or not _remote(policy["remote"]):
        raise ValueError("base branch, feature prefix, or remote is not a safe Git identity")
    if not policy["provenance"] or len(policy["provenance"]) != len(set(policy["provenance"])) or any(x not in DEFAULT_POLICY["provenance"] for x in policy["provenance"]):
        raise ValueError("provenance must be a nonempty supported subset")
    if policy["manual_merge"]["method"] not in ("squash", "merge", "rebase") or type(policy["manual_merge"]["require_current_turn_attestation"]) is not bool:
        raise ValueError("manual_merge method or attestation is invalid")
    if policy["pull_request"]["ready_policy"] not in ("auto", "ask", "keep-draft") or policy["pull_request"]["rejection_policy"] not in ("leave-open", "close-pr"):
        raise ValueError("pull-request policy is invalid")
    if policy["recovery"]["disambiguation"] != "block" or policy["recovery"]["selector"] != "exact-pr-url-or-number" or type(policy["recovery"]["require_exact_head"]) is not bool:
        raise ValueError("recovery policy is invalid")
    v = policy["validation"]
    if v["check_mode"] not in ("required", "all") or any(not _identifier(x) for x in v["check_names"] + v["visual_scenarios"]) or len(v["check_names"]) != len(set(v["check_names"])) or len(v["visual_scenarios"]) != len(set(v["visual_scenarios"])) or any(type(v[k]) is not int or v[k] < 0 for k in ("max_rechecks", "wait_seconds", "max_corrections")):
        raise ValueError("validation policy is invalid")
    if policy["remote_cleanup"] not in ("delete", "retain") or policy["issue_completion"] not in ("close", "comment-only", "none"):
        raise ValueError("completion policy is invalid")
    if policy["issue_completion"] == "close" and policy["remote_cleanup"] != "delete":
        raise ValueError("issue_completion close requires remote_cleanup delete")
    if type(policy["blocked_issue_creation"]) is not bool or policy["evidence"]["actor_transfer"] != "immutable-author-derived" or policy["evidence"]["require_authenticated_actor"] is not True or not _identifier(policy["evidence"]["current_id"]) or not _identifier(policy["evidence"]["completion_id"]) or policy["evidence"]["current_id"] == policy["evidence"]["completion_id"]:
        raise ValueError("immutable authenticated actor evidence is required")


def _identifier(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]{0,63}", value))


def _git_ref(value: str) -> bool:
    return bool(value) and not value.startswith(("/", "-", ".")) and not value.endswith(("/", ".", ".lock")) and ".." not in value and "@{" not in value and not any(character in value for character in " ~^:?*[\\\x00\r\n\t") and all(part not in ("", ".", "..") for part in value.split("/"))


def _remote(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value))

def policy_evidence(policy: dict) -> dict:
    rendered = {key: value for key, value in policy.items() if key != "_snapshot_digest"}
    return {"policy": rendered, "policy_digest": policy.get("_snapshot_digest")}


def policy_digest(path: str | None) -> str:
    """Return a digest only for the fixed lifecycle snapshot."""
    if path != SNAPSHOT_PATH:
        raise ValueError("policy path must be the fixed lifecycle policy snapshot")
    source = Path(path).read_bytes()
    return hashlib.sha256(source).hexdigest()
