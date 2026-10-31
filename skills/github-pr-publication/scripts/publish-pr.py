#!/usr/bin/env python3
"""Push the current branch and create one draft pull request."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse


def run(*args):
    return subprocess.run(args, text=True, capture_output=True, check=False)


def report(status, **evidence):
    print(json.dumps({"status": status, **evidence}, sort_keys=True))


def remote_identity(url):
    """Return a case-insensitive host and owner/repository identity."""
    value = url.strip().removesuffix("/").removesuffix(".git")
    if "://" in value:
        parsed = urlparse(value)
        host, path = parsed.hostname, parsed.path
    else:
        match = re.fullmatch(r"(?:[^@]+@)?([^:]+):(.+)", value)
        if not match:
            return None
        host, path = match.groups()
    parts = [part for part in path.split("/") if part]
    if not host or len(parts) != 2:
        return None
    return host.casefold(), "/".join(parts).casefold()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True, type=Path)
    parser.add_argument("--base", default="main")
    args = parser.parse_args()
    try:
        with args.body_file.open("rb"):
            pass
    except OSError as error:
        print(f"pull-request body file is not readable: {error}", file=sys.stderr)
        report("blocked", reason="body-file-unreadable")
        return 2
    branch = run("git", "branch", "--show-current")
    status = run("git", "status", "--porcelain=v1")
    if branch.returncode or status.returncode or not branch.stdout.strip() or branch.stdout.strip() == args.base or status.stdout:
        print("publication requires a clean committed non-base branch", file=sys.stderr)
        report("blocked", reason="branch-or-worktree-prerequisite")
        return 2
    branch_name = branch.stdout.strip()
    head = run("git", "rev-parse", "--verify", "HEAD")
    base = run("git", "rev-parse", "--verify", f"refs/heads/{args.base}")
    origin = run("git", "remote", "get-url", "origin")
    auth = run("gh", "auth", "status")
    repository = run("gh", "repo", "view", "--json", "nameWithOwner,url")
    if any(command.returncode for command in (head, base, origin, auth, repository)):
        print("publication prerequisites could not establish repository, base, head, origin, or authentication", file=sys.stderr)
        report("blocked", reason="publication-prerequisite")
        return 2
    try:
        repository_evidence = json.loads(repository.stdout)
    except json.JSONDecodeError:
        print("GitHub repository evidence was not valid JSON", file=sys.stderr)
        report("blocked", reason="repository-evidence-invalid")
        return 2
    if not isinstance(repository_evidence, dict) or not all(
        isinstance(repository_evidence.get(field), str) and repository_evidence[field]
        for field in ("nameWithOwner", "url")
    ):
        print("GitHub repository evidence was incomplete", file=sys.stderr)
        report("blocked", reason="repository-evidence-invalid")
        return 2
    origin_identity = remote_identity(origin.stdout)
    repository_identity = remote_identity(repository_evidence["url"])
    if origin_identity is None or origin_identity != repository_identity or origin_identity[1] != repository_evidence["nameWithOwner"].casefold():
        print("origin does not match the verified GitHub repository", file=sys.stderr)
        report("blocked", reason="repository-origin-mismatch")
        return 2
    owner_repo = repository_evidence["nameWithOwner"]
    existing = run("gh", "pr", "list", "--repo", owner_repo, "--head", branch_name, "--state", "all", "--json", "number,url,state,headRefOid")
    if existing.returncode:
        print("existing pull-request state could not be established", file=sys.stderr)
        report("blocked", reason="existing-pull-request-unknown", branch=branch_name, head=head.stdout.strip())
        return 2
    try:
        pull_requests = json.loads(existing.stdout)
    except json.JSONDecodeError:
        print("existing pull-request evidence was not valid JSON", file=sys.stderr)
        report("blocked", reason="existing-pull-request-evidence-invalid", branch=branch_name, head=head.stdout.strip())
        return 2
    if not isinstance(pull_requests, list) or any(not isinstance(item, dict) for item in pull_requests):
        print("existing pull-request evidence had an invalid shape", file=sys.stderr)
        report("blocked", reason="existing-pull-request-evidence-invalid", branch=branch_name, head=head.stdout.strip())
        return 2
    evidence = {
        "base": args.base,
        "base_head": base.stdout.strip(),
        "branch": branch_name,
        "head": head.stdout.strip(),
        "origin": origin.stdout.strip(),
        "repository": repository_evidence,
    }
    if len(pull_requests) != 0:
        report("blocked", reason="existing-pull-request", pull_requests=pull_requests, **evidence)
        return 2
    pushed = run("git", "push", "--set-upstream", "origin", branch_name)
    if pushed.returncode:
        print("publication status: not-published; branch-push-failed", file=sys.stderr)
        print(pushed.stderr, file=sys.stderr)
        report("not-published", reason="branch-push-failed", **evidence)
        return pushed.returncode
    created = run("gh", "pr", "create", "--repo", owner_repo, "--draft", "--base", args.base, "--head", branch_name, "--title", args.title, "--body-file", str(args.body_file))
    if created.returncode:
        print("publication status: branch-pushed; pull-request-not-created; do not retry automatically", file=sys.stderr)
        print(created.stderr, file=sys.stderr)
        report("partial", reason="branch-pushed; pull-request-not-created", **evidence)
        return created.returncode
    print("publication status: branch-pushed; pull-request-created")
    report("published", pull_request_url=created.stdout.strip(), **evidence)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
