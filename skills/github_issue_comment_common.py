"""Fail-closed validation for lifecycle-owned GitHub issue comments."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def comment_author_matches(comment: dict, actor: str) -> bool:
    author = comment.get("author")
    return isinstance(author, dict) and (author.get("login") or "").casefold() == actor.casefold()


def exact_controlled_line(lines: list[str], prefix: str, expected: str) -> bool:
    return [line for line in lines if line.startswith(prefix)] == [expected]


def visual_evidence_matches(lines: list[str]) -> bool:
    visual = [line for line in lines if line.startswith("Visual evidence:")]
    if visual == ["Visual evidence: not required"]:
        return not any(line.startswith("![Before:") or line.startswith("![After:") for line in lines)
    if visual != ["Visual evidence: passed"]:
        return False
    before = [line for line in lines if line.startswith("![Before:")]
    after = [line for line in lines if line.startswith("![After:")]
    if len(before) != 1 or len(after) != 1:
        return False
    before_match = re.fullmatch(r"!\[Before: ([^\]]+)\]\((https://[^)]+)\)", before[0])
    after_match = re.fullmatch(r"!\[After: ([^\]]+)\]\((https://[^)]+)\)", after[0])
    if before_match is None or after_match is None or before_match.group(1) != after_match.group(1):
        return False
    urls = (urlparse(before_match.group(2)), urlparse(after_match.group(2)))
    return all(url.hostname == "github.com" and url.path.startswith("/user-attachments/") for url in urls)


def current_comment_matches(comment: dict, url: str, head: str, actor: str) -> bool:
    lines = (comment.get("body") or "").splitlines()
    delivered = [line for line in lines if line.startswith("Delivered outcome:")]
    return (
        comment_author_matches(comment, actor)
        and exact_controlled_line(lines, "Lifecycle evidence:", "Lifecycle evidence: current")
        and len(delivered) == 1
        and bool(delivered[0].removeprefix("Delivered outcome:").strip())
        and exact_controlled_line(lines, "Pull request:", f"Pull request: {url}")
        and exact_controlled_line(lines, "Head commit:", f"Head commit: {head}")
        and exact_controlled_line(lines, "Delegate project-validation:", "Delegate project-validation: passed")
        and exact_controlled_line(lines, "Required checks:", "Required checks: passed")
        and visual_evidence_matches(lines)
    )


def completion_comment_matches(comment: dict, url: str, head: str, actor: str) -> bool:
    lines = (comment.get("body") or "").splitlines()
    cleanup = {"Remote cleanup: deleted", "Remote cleanup: already-absent"}
    return (
        comment_author_matches(comment, actor)
        and exact_controlled_line(lines, "Lifecycle completion:", "Lifecycle completion: merged-pr")
        and exact_controlled_line(lines, "Pull request:", f"Pull request: {url}")
        and exact_controlled_line(lines, "Head commit:", f"Head commit: {head}")
        and exact_controlled_line(lines, "Merge result:", "Merge result: merged")
        and exact_controlled_line(lines, "Delegate project-validation:", "Delegate project-validation: passed")
        and exact_controlled_line(lines, "Required checks:", "Required checks: passed")
        and sum(line in cleanup for line in lines) == 1
        and len([line for line in lines if line.startswith("Remote cleanup:")]) == 1
    )
