"""Fail-closed shared primitives for GitHub pull-request lifecycle scripts.

This module performs no Git or GitHub mutation.  Lifecycle operation predicates and
mutations remain in their owning scripts.
"""
from __future__ import annotations

import json
import subprocess
from urllib.parse import urlparse

VERSION = 1


def run(args: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, input=input_text, text=True, capture_output=True, check=False)


def emit(status: str, disposition: str, evidence: dict, blocker: str | None = None, next_stage: str | None = None, *, repair_exit: int = 4) -> int:
    """Emit the version-1 lifecycle result envelope without changing its shape."""
    print(json.dumps({"version": VERSION, "status": status, "disposition": disposition,
                      "next_stage": next_stage, "evidence": evidence, "blocker": blocker}, sort_keys=True))
    return 0 if status == "passed" else 3 if status == "waiting" else repair_exit if status == "repair" else 2


def parse_object(completed: subprocess.CompletedProcess[str]) -> dict | None:
    if completed.returncode != 0:
        return None
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def parse_list(stdout: str) -> list[dict] | None:
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, list) and all(isinstance(item, dict) for item in value) else None


def verified_checkout(run_command, evidence: dict) -> tuple[str, dict | None, str | None]:
    """Verify auth and repository identity; return waiting, blocked, or passed."""
    auth = run_command(["gh", "auth", "status"])
    repo = run_command(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    if auth.returncode != 0 or repo.returncode != 0:
        return "waiting", None, (auth.stderr or repo.stderr).strip()
    repository = parse_object(repo)
    if not repository or not repository.get("nameWithOwner") or not repository.get("url"):
        return "blocked", None, "repository identity is malformed or incomplete"
    evidence["repository"] = repository
    return "passed", repository, None


def repository_matches(repository: dict, pull_request: dict) -> bool:
    number = pull_request.get("number")
    repository_url = (repository.get("url") or "").rstrip("/")
    return bool(repository.get("nameWithOwner")) and bool(repository_url) and type(number) is int and number > 0 and pull_request.get("url") == f"{repository_url}/pull/{number}"


def remote_repository_matches(repository: dict, remote_url: str) -> bool:
    expected_url = urlparse(repository.get("url") or "")
    expected_name = (repository.get("nameWithOwner") or "").strip("/")
    remote_url = remote_url.strip()
    if "://" in remote_url:
        parsed = urlparse(remote_url)
        host, path = parsed.hostname or "", parsed.path
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
    return pull_request.get("isCrossRepository") is False and isinstance(head_repository, dict) and (head_repository.get("nameWithOwner") or "").casefold() == (repository.get("nameWithOwner") or "").casefold()


def parse_remote_head(stdout: str, branch: str | None = None) -> tuple[str | None, bool]:
    lines = [line.split() for line in stdout.splitlines() if line.strip()]
    if not lines:
        return None, True
    if len(lines) != 1 or len(lines[0]) != 2 or branch and lines[0][1] != f"refs/heads/{branch}":
        return None, False
    return lines[0][0], True


def marker_matches(record: dict, provenance: str, issue: str | None = None) -> bool:
    lines = (record.get("body") or "").splitlines()
    origins = [line for line in lines if line.startswith("OpenCode-Origin:")]
    references = [line for line in lines if line.startswith("Refs #")]
    if origins != [f"OpenCode-Origin: {provenance}"]:
        return False
    return references == [f"Refs #{issue.lstrip('#') if issue else ''}"] if provenance == "github-issue" else not references


def pull_request_repositories_match(repository: dict, pull_request: dict) -> bool:
    return repository_matches(repository, pull_request) and head_repository_matches(repository, pull_request)
