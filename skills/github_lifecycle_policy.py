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
    },
    "manual_merge": {"method": "squash"},
    "pull_request": {"ready_policy": "auto", "rejection_policy": "leave-open"},
    "recovery": {"disambiguation": "block", "selector": "exact-pr-url-or-number"},
    "validation": {"check_mode": "required", "check_names": [], "max_rechecks": 5, "wait_seconds": 30, "max_corrections": 1, "visual_scenarios": []},
    "remote_cleanup": "delete",
    "issue_completion": "close",
    "blocked_issue_creation": False,
}
SNAPSHOT_DIRECTORY = Path("/tmp/opencode")


def snapshot_path(repository: str, lifecycle_run: str) -> str:
    """Return the sole safe snapshot path for one repository/run pair."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("repository binding is invalid")
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{7,63}", lifecycle_run):
        raise ValueError("lifecycle run identity is invalid")
    repository_token = hashlib.sha256(repository.casefold().encode()).hexdigest()[:16]
    return str(SNAPSHOT_DIRECTORY / f"lifecycle-policy.{repository_token}.{lifecycle_run}.snapshot.json")

def add_policy_argument(parser) -> None:
    parser.add_argument("--policy", required=True, help="repository-and-run-bound immutable lifecycle policy snapshot")
    parser.add_argument("--expected-policy-digest", required=True, help="SHA-256 of the immutable resolved policy snapshot")
    parser.add_argument("--repository", required=True, help="exact owner/name repository identity bound to this run")
    parser.add_argument("--lifecycle-run", required=True, help="opaque immutable lifecycle run identity")

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

def load_policy(path: str | None, expected_digest: str | None, repository: str, lifecycle_run: str) -> dict:
    """Load only the exact immutable snapshot bound to one repository and run."""
    if path != snapshot_path(repository, lifecycle_run):
        raise ValueError("policy path must be the repository-and-run-bound lifecycle policy snapshot")
    if not expected_digest or not re.fullmatch(r"[0-9a-f]{64}", expected_digest):
        raise ValueError("expected lifecycle policy snapshot digest is required")
    try:
        source = Path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f"invalid lifecycle policy: {exc}") from exc
    digest = hashlib.sha256(source).hexdigest()
    if digest != expected_digest:
        raise ValueError("policy snapshot digest does not match the expected digest")
    policy = _load_normalized_policy(source, digest)
    binding = policy.get("_binding")
    if binding != {"repository": repository, "lifecycle_run": lifecycle_run}:
        raise ValueError("policy snapshot binding does not match this repository and lifecycle run")
    return policy


def resolve_policy_source(source: bytes | None, repository: str, lifecycle_run: str) -> tuple[dict, bytes, str]:
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
    snapshot_path(repository, lifecycle_run)
    policy["_binding"] = {"repository": repository, "lifecycle_run": lifecycle_run}
    normalized = json.dumps(policy, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    digest = hashlib.sha256(normalized).hexdigest()
    policy["_snapshot_digest"] = digest
    return policy, normalized, digest


def _load_normalized_policy(source: bytes, digest: str) -> dict:
    decoded = json.loads(source)
    binding = decoded.get("_binding") if isinstance(decoded, dict) else None
    if binding is not None and (not isinstance(binding, dict) or set(binding) != {"repository", "lifecycle_run"}):
        raise ValueError("lifecycle policy binding is invalid")
    if binding is not None:
        assert isinstance(decoded, dict)
        decoded = dict(decoded)
        del decoded["_binding"]
        source_without_binding = json.dumps(decoded, sort_keys=True, separators=(",", ":")).encode()
    else:
        source_without_binding = source
    if binding is None:
        raise ValueError("repository and lifecycle-run bindings are required for this policy snapshot")
    policy, normalized, normalized_digest = resolve_policy_source(source_without_binding, binding["repository"], binding["lifecycle_run"])
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
    if policy["manual_merge"]["method"] not in ("squash", "merge", "rebase"):
        raise ValueError("manual_merge method is invalid")
    if policy["pull_request"]["ready_policy"] not in ("auto", "ask", "keep-draft") or policy["pull_request"]["rejection_policy"] != "leave-open":
        raise ValueError("pull-request policy is invalid")
    if policy["recovery"]["disambiguation"] != "block" or policy["recovery"]["selector"] != "exact-pr-url-or-number":
        raise ValueError("recovery policy is invalid")
    v = policy["validation"]
    if v["check_mode"] not in ("required", "all") or any(not _check_name(x) for x in v["check_names"]) or any(not _identifier(x) for x in v["visual_scenarios"]) or len(v["check_names"]) != len(set(v["check_names"])) or len(v["visual_scenarios"]) != len(set(v["visual_scenarios"])) or any(type(v[k]) is not int or v[k] < 0 for k in ("max_rechecks", "wait_seconds", "max_corrections")):
        raise ValueError("validation policy is invalid")
    if policy["remote_cleanup"] not in ("delete", "retain") or policy["issue_completion"] not in ("close", "comment-only", "none"):
        raise ValueError("completion policy is invalid")
    if policy["issue_completion"] == "close" and policy["remote_cleanup"] != "delete":
        raise ValueError("issue_completion close requires remote_cleanup delete")
    if type(policy["blocked_issue_creation"]) is not bool or policy["evidence"]["require_authenticated_actor"] is not True or not _identifier(policy["evidence"]["current_id"]) or not _identifier(policy["evidence"]["completion_id"]) or policy["evidence"]["current_id"] == policy["evidence"]["completion_id"]:
        raise ValueError("immutable authenticated actor evidence is required")


def _identifier(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9._-]{0,63}", value))


def _check_name(value: object) -> bool:
    """GitHub check names are display labels, not machine identifiers."""
    return isinstance(value, str) and bool(value.strip()) and len(value) <= 200 and "\x00" not in value and "\n" not in value and "\r" not in value


def _git_ref(value: str) -> bool:
    return bool(value) and not value.startswith(("/", "-", ".")) and not value.endswith(("/", ".", ".lock")) and ".." not in value and "@{" not in value and not any(character in value for character in " ~^:?*[\\\x00\r\n\t") and all(part not in ("", ".", "..") for part in value.split("/"))


def _remote(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}", value))

def policy_evidence(policy: dict) -> dict:
    rendered = {key: value for key, value in policy.items() if key != "_snapshot_digest"}
    return {"policy": rendered, "policy_digest": policy.get("_snapshot_digest"), "policy_binding": policy.get("_binding")}


def policy_digest(path: str | None, repository: str, lifecycle_run: str) -> str:
    """Return a digest only for an exact repository/run-bound snapshot."""
    if path != snapshot_path(repository, lifecycle_run):
        raise ValueError("policy path must be the repository-and-run-bound lifecycle policy snapshot")
    source = Path(path).read_bytes()
    return hashlib.sha256(source).hexdigest()
