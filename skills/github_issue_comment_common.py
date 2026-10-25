"""Fail-closed validation for lifecycle-owned GitHub issue comments."""

from __future__ import annotations

import re
from urllib.parse import urlparse


def comment_author_matches(comment: dict, actor: str) -> bool:
    author = comment.get("author")
    return isinstance(author, dict) and (author.get("login") or "").casefold() == actor.casefold()


def exact_controlled_line(lines: list[str], prefix: str, expected: str) -> bool:
    return [line for line in lines if line.startswith(prefix)] == [expected]


def visual_evidence_matches(lines: list[str], scenarios: list[str] | None = None) -> bool:
    """Require one uploaded, accessible before/after pair for every policy scenario."""
    scenarios = scenarios or []
    visual = [line for line in lines if line.startswith("Visual evidence:")]
    if visual == ["Visual evidence: not required"]:
        # An empty policy is the lifecycle's explicit browser-impact-nonapplicable
        # state. A configured scenario always requires concrete evidence.
        return not scenarios and not any(line.startswith("![Before:") or line.startswith("![After:") for line in lines)
    if visual != ["Visual evidence: passed"]:
        return False
    before = [line for line in lines if line.startswith("![Before:")]
    after = [line for line in lines if line.startswith("![After:")]
    if len(before) != len(scenarios) or len(after) != len(scenarios):
        return False
    before_pairs = [re.fullmatch(r"!\[Before: ([^\]]+)\]\((https://[^)]+)\)", line) for line in before]
    after_pairs = [re.fullmatch(r"!\[After: ([^\]]+)\]\((https://[^)]+)\)", line) for line in after]
    if any(pair is None for pair in before_pairs + after_pairs):
        return False
    assert all(pair is not None for pair in before_pairs + after_pairs)
    before_by_scenario = {pair.group(1): pair.group(2) for pair in before_pairs}
    after_by_scenario = {pair.group(1): pair.group(2) for pair in after_pairs}
    if set(before_by_scenario) != set(scenarios) or set(after_by_scenario) != set(scenarios):
        return False
    if len(before_by_scenario) != len(before_pairs) or len(after_by_scenario) != len(after_pairs):
        return False
    # A screenshot may prove exactly one phase of one scenario.  Reuse would
    # make a policy-wide manifest look complete while losing scenario evidence.
    urls = [*before_by_scenario.values(), *after_by_scenario.values()]
    if len(urls) != len(set(urls)):
        return False
    return all(
        urlparse(url).scheme == "https"
        and urlparse(url).hostname == "github.com"
        and urlparse(url).path.startswith("/user-attachments/")
        for url in urls
    )


def current_comment_matches(comment: dict, url: str, head: str, actor: str, policy: dict | None = None) -> bool:
    policy = policy or {"evidence": {"current_id": "current"}, "validation": {"visual_scenarios": []}}
    lines = (comment.get("body") or "").splitlines()
    delivered = [line for line in lines if line.startswith("Delivered outcome:")]
    return (
        comment_author_matches(comment, actor)
        and exact_controlled_line(lines, "Lifecycle evidence:", f"Lifecycle evidence: {policy['evidence']['current_id']}")
        and len(delivered) == 1
        and bool(delivered[0].removeprefix("Delivered outcome:").strip())
        and exact_controlled_line(lines, "Pull request:", f"Pull request: {url}")
        and exact_controlled_line(lines, "Head commit:", f"Head commit: {head}")
        and exact_controlled_line(lines, "Delegate project-validation:", "Delegate project-validation: passed")
        and exact_controlled_line(lines, "Required checks:", "Required checks: passed")
        and visual_evidence_matches(lines, policy["validation"]["visual_scenarios"])
    )


def completion_comment_matches(comment: dict, url: str, head: str, actor: str, policy: dict | None = None) -> bool:
    policy = policy or {"evidence": {"completion_id": "merged-pr"}}
    lines = (comment.get("body") or "").splitlines()
    cleanup = {"Remote cleanup: deleted", "Remote cleanup: already-absent"}
    if policy and policy.get("remote_cleanup") == "retain":
        cleanup.add("Remote cleanup: retained")
    return (
        comment_author_matches(comment, actor)
        and exact_controlled_line(lines, "Lifecycle completion:", f"Lifecycle completion: {policy['evidence']['completion_id']}")
        and exact_controlled_line(lines, "Pull request:", f"Pull request: {url}")
        and exact_controlled_line(lines, "Head commit:", f"Head commit: {head}")
        and exact_controlled_line(lines, "Merge result:", "Merge result: merged")
        and exact_controlled_line(lines, "Delegate project-validation:", "Delegate project-validation: passed")
        and exact_controlled_line(lines, "Required checks:", "Required checks: passed")
        and sum(line in cleanup for line in lines) == 1
        and len([line for line in lines if line.startswith("Remote cleanup:")]) == 1
    )
