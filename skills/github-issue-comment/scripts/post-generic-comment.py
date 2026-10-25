#!/usr/bin/env python3
"""Post one non-lifecycle issue comment with exact idempotency verification."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_pr_lifecycle_common import emit, parse_object, run

BODY = Path("/tmp/opencode/github-issue-manager-comment.md")

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    parser.add_argument("--identity", required=True)
    parser.add_argument("--authorize-comment", action="store_true")
    args = parser.parse_args()
    if not args.authorize_comment:
        return emit("waiting", "waiting-user-authorization", {}, "explicit generic comment authorization is required")
    try:
        body = BODY.read_text()
    except OSError as exc:
        return emit("blocked", "blocked-unsafe", {}, f"generic comment body is unavailable: {exc}")
    if [line for line in body.splitlines() if line.startswith("OpenCode-Comment-ID:")] != [f"OpenCode-Comment-ID: {args.identity}"]:
        return emit("blocked", "blocked-unsafe", {}, "generic comment requires one exact idempotency identity")
    if any(line.startswith(("Lifecycle evidence:", "Lifecycle completion:")) for line in body.splitlines()):
        return emit("blocked", "blocked-unsafe", {}, "lifecycle markers require github-lifecycle-issue-evidence")
    repo = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
    repository = parse_object(repo)
    if not repository:
        return emit("waiting", "waiting-external", {}, repo.stderr.strip() or "repository unavailable")
    def read_issue():
        return parse_object(run(["gh", "issue", "view", args.issue, "--repo", repository["nameWithOwner"], "--json", "number,url,state,comments"]))
    before = read_issue()
    if not before:
        return emit("waiting", "waiting-external", {"repository": repository}, "issue unavailable")
    matches = [comment for comment in before.get("comments", []) if f"OpenCode-Comment-ID: {args.identity}" in (comment.get("body") or "").splitlines()]
    if len(matches) == 1 and matches[0].get("body") == body:
        return emit("passed", "reused", {"repository": repository, "comment": matches[0]})
    if matches:
        return emit("blocked", "blocked-unsafe", {"repository": repository}, "generic comment identity conflicts")
    posted = run(["gh", "issue", "comment", args.issue, "--repo", repository["nameWithOwner"], "--body-file", str(BODY)])
    after = read_issue()
    new = [comment for comment in (after or {}).get("comments", []) if f"OpenCode-Comment-ID: {args.identity}" in (comment.get("body") or "").splitlines() and comment.get("body") == body]
    if len(new) != 1:
        return emit("waiting", "waiting-external", {"repository": repository}, posted.stderr.strip() or "generic comment post was not verified")
    return emit("passed", "posted", {"repository": repository, "comment": new[0]})
if __name__ == "__main__": raise SystemExit(main())
