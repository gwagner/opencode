#!/usr/bin/env python3
"""Post one repository-bound GitHub issue comment with durable idempotency."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from github_lifecycle_policy import add_authorization_argument, add_policy_argument, authorized, load_policy, policy_evidence
from github_issue_comment_common import completion_comment_matches, current_comment_matches
from github_pr_lifecycle_common import emit as result_emit, parse_object, run

BODY_FILE = Path("/tmp/opencode/github-issue-manager-comment.md")


def issue_matches(repository: dict, issue: dict) -> bool:
    number = issue.get("number")
    return type(number) is int and number > 0 and issue.get("url") == f"{repository.get('url', '').rstrip('/')}/issues/{number}"


def valid_comment_shape(comment: dict) -> bool:
    return (
        bool(comment.get("id"))
        and bool(comment.get("url"))
        and isinstance(comment.get("body"), str)
        and isinstance(comment.get("author"), dict)
        and bool(comment["author"].get("login"))
    )


def attachment_parts(value: str) -> tuple[str, str] | None:
    path, separator, alt = value.partition("#")
    resolved = Path(path)
    if not separator or not alt or not resolved.is_absolute() or not resolved.is_relative_to("/tmp/opencode"):
        return None
    return path, alt


def validate_visual_manifest(value: object, scenarios: list[str]) -> dict[str, dict[str, str]] | None:
    """Validate the exact, real local evidence pair required per configured scenario."""
    if not isinstance(value, dict) or set(value) != set(scenarios):
        return None
    manifest: dict[str, dict[str, str]] = {}
    artifact_paths: set[Path] = set()
    for scenario in scenarios:
        pair = value.get(scenario)
        if not isinstance(pair, dict) or set(pair) != {"before", "after"}:
            return None
        normalized: dict[str, str] = {}
        for phase in ("before", "after"):
            path = pair[phase]
            if not isinstance(path, str) or not path or "#" in path:
                return None
            candidate = Path(path)
            resolved = candidate.resolve()
            if not candidate.is_absolute() or not resolved.is_relative_to("/tmp/opencode") or not resolved.is_file():
                return None
            normalized[phase] = path
        # A pair cannot make a meaningful before/after claim from one artifact.
        if Path(normalized["before"]).resolve() == Path(normalized["after"]).resolve():
            return None
        resolved_pair = {Path(normalized["before"]).resolve(), Path(normalized["after"]).resolve()}
        if artifact_paths.intersection(resolved_pair):
            return None
        artifact_paths.update(resolved_pair)
        manifest[scenario] = normalized
    return manifest


def local_visual_body_matches(body: str, attachments: list[str], manifest: dict[str, dict[str, str]]) -> bool:
    parts = [attachment_parts(value) for value in attachments]
    expected_attachments = [
        f"{manifest[scenario][phase]}#{phase.title()}: {scenario}"
        for scenario in manifest
        for phase in ("before", "after")
    ]
    if attachments != expected_attachments or any(part is None for part in parts):
        return False
    lines = body.splitlines()
    visual = [line for line in lines if line.startswith("Visual evidence:")]
    before = [line for line in lines if line.startswith("![Before:")]
    after = [line for line in lines if line.startswith("![After:")]
    if visual != ["Visual evidence: passed"] or len(before) != len(manifest) or len(after) != len(manifest):
        return False
    expected_lines = {
        f"![{phase.title()}: {scenario}]({manifest[scenario][phase]})"
        for scenario in manifest
        for phase in ("before", "after")
    }
    return set(before + after) == expected_lines and len(set(before + after)) == len(expected_lines)


def lifecycle_candidate(comment: dict, kind: str, policy: dict | None = None) -> bool:
    policy = policy or {"evidence": {"current_id": "current", "completion_id": "merged-pr"}}
    prefix = f"Lifecycle evidence: {policy['evidence']['current_id']}" if kind == "current" else f"Lifecycle completion: {policy['evidence']['completion_id']}"
    return any(line.startswith(prefix) for line in (comment.get("body") or "").splitlines())


def attached_body_matches(expected: str, actual: str, attachments: list[str]) -> bool:
    expected_normalized = expected
    actual_normalized = actual
    for value in attachments:
        part = attachment_parts(value)
        if part is None:
            return False
        path, alt = part
        image_marker = f"![{alt}]({path})"
        link_marker = f"[{alt}]({path})"
        is_image = expected_normalized.count(image_marker) == 1
        expected_marker = image_marker if is_image else link_marker
        bang = "!" if is_image else ""
        match = re.search(rf"{bang}\[{re.escape(alt)}\]\((https://[^)]+)\)", actual_normalized)
        if expected_normalized.count(expected_marker) != 1 or match is None:
            return False
        parsed = urlparse(match.group(1))
        if parsed.hostname != "github.com" or not parsed.path.startswith("/user-attachments/"):
            return False
        placeholder = f"{bang}[{alt}](<uploaded>)"
        expected_normalized = expected_normalized.replace(expected_marker, placeholder)
        actual_normalized = actual_normalized.replace(match.group(0), placeholder)
    return expected_normalized == actual_normalized


def local_attachment_body_matches(body: str, attachments: list[str]) -> bool:
    parts = [attachment_parts(value) for value in attachments]
    return bool(parts) and all(
        part is not None
        and len(re.findall(rf"!?\[{re.escape(part[1])}\]\({re.escape(part[0])}\)", body)) == 1
        for part in parts
    )


def lifecycle_body_matches(body: str, kind: str, pr: str, head: str, attachments: list[str], visual_manifest: dict[str, dict[str, str]] | None, policy: dict | None = None) -> bool:
    actor = "preflight"
    comment = {"author": {"login": actor}, "body": body}
    if kind == "completion":
        return not attachments and completion_comment_matches(comment, pr, head, actor, policy)
    scenarios = policy["validation"]["visual_scenarios"]
    if not scenarios:
        return visual_manifest is None and not attachments and current_comment_matches(comment, pr, head, actor, policy)
    if visual_manifest is None or not local_visual_body_matches(body, attachments, visual_manifest):
        return False
    uploaded_body = re.sub(r"\]\([^)]+\)", "](https://github.com/user-attachments/assets/preflight)", body)
    return current_comment_matches({"author": {"login": actor}, "body": uploaded_body}, pr, head, actor, policy)


def exact_existing_match(comment: dict, kind: str, body: str, actor: str, pr: str | None, head: str | None, attachments: list[str], policy: dict | None = None) -> bool:
    if (comment.get("author", {}).get("login") or "").casefold() != actor.casefold():
        return False
    if kind == "generic":
        return attached_body_matches(body, comment.get("body") or "", attachments) if attachments else comment.get("body") == body
    assert pr is not None and head is not None
    validator = current_comment_matches if kind == "current" else completion_comment_matches
    if not validator(comment, pr, head, actor, policy):
        return False
    if kind == "completion" or "Visual evidence: not required" in body.splitlines():
        return comment.get("body") == body
    return attached_body_matches(body, comment.get("body") or "", attachments)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    parser.add_argument("--identity", required=True)
    parser.add_argument("--kind", choices=("current", "completion"), required=True)
    parser.add_argument("--pr")
    parser.add_argument("--head")
    parser.add_argument("--attach", action="append", default=[])
    parser.add_argument("--visual-manifest")
    add_policy_argument(parser)
    add_authorization_argument(parser, "comment")
    args = parser.parse_args()
    try:
        policy = load_policy(args.policy, args.expected_policy_digest, args.repository, args.lifecycle_run)
    except ValueError as exc:
        return result_emit("blocked", "blocked-unsafe", {}, str(exc))
    evidence: dict[str, object] = {**policy_evidence(policy), "identity": args.identity, "kind": args.kind}
    if not authorized(policy, "comment", args.authorize_comment):
        return result_emit("blocked", "blocked-unsafe", evidence, "explicit comment authorization is required")
    visual_manifest = None
    if args.visual_manifest:
        try:
            manifest = json.loads(Path(args.visual_manifest).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            return result_emit("blocked", "blocked-unsafe", evidence, f"invalid visual manifest: {exc}")
        visual_manifest = validate_visual_manifest(manifest, policy["validation"]["visual_scenarios"])
        if visual_manifest is None:
            return result_emit("blocked", "blocked-unsafe", evidence, "visual manifest must contain the exact configured scenarios and real distinct /tmp/opencode before/after paths")
        evidence["visual_manifest"] = visual_manifest
    try:
        body = BODY_FILE.read_text()
        if not body:
            return result_emit("blocked", "blocked-unsafe", evidence, "comment body is empty")
        if args.kind == "generic":
            expected_identity = f"OpenCode-Comment-ID: {args.identity}"
            if [line for line in body.splitlines() if line.startswith("OpenCode-Comment-ID:")] != [expected_identity]:
                return result_emit("blocked", "blocked-unsafe", evidence, "generic comment identity is missing or conflicting")
            if any(line.startswith("Lifecycle evidence:") or line.startswith("Lifecycle completion:") for line in body.splitlines()):
                return result_emit("blocked", "blocked-unsafe", evidence, "lifecycle-controlled markers require lifecycle comment validation")
            if args.attach and not local_attachment_body_matches(body, args.attach):
                return result_emit("blocked", "blocked-unsafe", evidence, "generic attachment identity is invalid")
        elif not args.pr or not args.head or args.identity != f"{args.kind}:{args.pr}:{args.head}" or not lifecycle_body_matches(body, args.kind, args.pr, args.head, args.attach, visual_manifest, policy):
            return result_emit("blocked", "blocked-unsafe", evidence, "lifecycle comment body, identity, or attachments are invalid")

        auth = run(["gh", "auth", "status"])
        repo_result = run(["gh", "repo", "view", "--json", "nameWithOwner,url"])
        if auth.returncode != 0 or repo_result.returncode != 0:
            return result_emit("waiting", "waiting-external", evidence, (auth.stderr or repo_result.stderr).strip())
        repository = parse_object(repo_result)
        if not repository or not repository.get("nameWithOwner") or not repository.get("url"):
            return result_emit("blocked", "blocked-unsafe", evidence, "repository identity is malformed")
        host = urlparse(repository["url"]).hostname
        if not host:
            return result_emit("blocked", "blocked-unsafe", evidence, "repository host is missing")
        actor_result = run(["gh", "api", "--hostname", host, "user", "--jq", ".login"])
        if actor_result.returncode != 0:
            return result_emit("waiting", "waiting-external", evidence, actor_result.stderr.strip())
        actor = actor_result.stdout.strip()
        if not actor:
            return result_emit("blocked", "blocked-unsafe", evidence, "authenticated actor is missing")
        if args.attach:
            help_result = run(["gh", "issue", "comment", "--help"])
            if help_result.returncode != 0 or "--attach" not in help_result.stdout:
                return result_emit("blocked", "blocked-unsafe", evidence, "GitHub CLI does not support native issue-comment attachments")

        def read_issue() -> tuple[dict | None, str | None]:
            viewed = run(["gh", "issue", "view", args.issue, "--repo", repository["nameWithOwner"], "--json", "number,title,state,url,comments"])
            if viewed.returncode != 0:
                return None, viewed.stderr.strip()
            record = parse_object(viewed)
            return record, None

        issue, error = read_issue()
        if error:
            return result_emit("waiting", "waiting-external", evidence, error)
        if not issue or not issue_matches(repository, issue):
            return result_emit("blocked", "blocked-unsafe", evidence, "issue does not belong to the checkout repository")
        comments = issue.get("comments")
        if not isinstance(comments, list) or any(not isinstance(comment, dict) or not valid_comment_shape(comment) for comment in comments):
            return result_emit("blocked", "blocked-unsafe", evidence, "issue comments lack stable identity fields")
        ids = [comment["id"] for comment in comments]
        if len(ids) != len(set(ids)):
            return result_emit("blocked", "blocked-unsafe", evidence, "issue comment IDs are duplicated")

        if args.kind == "generic":
            candidates = [comment for comment in comments if f"OpenCode-Comment-ID: {args.identity}" in comment["body"].splitlines()]
        else:
            assert args.pr is not None and args.head is not None
            current_comments = [comment for comment in comments if lifecycle_candidate(comment, "current", policy)]
            completion_comments = [comment for comment in comments if lifecycle_candidate(comment, "completion", policy)]
            if any(not current_comment_matches(comment, args.pr, args.head, actor, policy) for comment in current_comments):
                return result_emit("blocked", "blocked-unsafe", evidence, "current lifecycle evidence is malformed or has the wrong actor")
            if any(not completion_comment_matches(comment, args.pr, args.head, actor, policy) for comment in completion_comments):
                return result_emit("blocked", "blocked-unsafe", evidence, "completion lifecycle evidence is malformed or has the wrong actor")
            if len({comment["body"] for comment in current_comments}) > 1 or len({comment["body"] for comment in completion_comments}) > 1:
                return result_emit("blocked", "blocked-unsafe", evidence, "lifecycle evidence conflicts")
            if args.kind == "current" and completion_comments:
                return result_emit("blocked", "blocked-unsafe", evidence, "completion evidence exists before current evidence is established")
            if args.kind == "completion" and not current_comments:
                return result_emit("blocked", "blocked-unsafe", evidence, "completion comment requires exact current lifecycle evidence")
            candidates = [comment for comment in comments if lifecycle_candidate(comment, args.kind, policy)]
        matches = [comment for comment in candidates if exact_existing_match(comment, args.kind, body, actor, args.pr, args.head, args.attach, policy)]
        if candidates and len(matches) != len(candidates):
            return result_emit("blocked", "blocked-unsafe", evidence, "comment idempotency identity conflicts with existing evidence")
        if len(matches) == 1:
            evidence["comment"] = matches[0]
            return result_emit("passed", "reused", evidence)
        if len(matches) > 1:
            return result_emit("blocked", "blocked-unsafe", evidence, "comment idempotency identity is ambiguous")

        command = ["gh", "issue", "comment", args.issue, "--repo", repository["nameWithOwner"], "--body-file", str(BODY_FILE)]
        for attachment in args.attach:
            command.extend(["--attach", attachment])
        posted = run(command)
        after_issue, after_error = read_issue()
        if after_error:
            return result_emit("waiting", "waiting-external", evidence, after_error)
        after_comments = after_issue.get("comments") if after_issue else None
        if not after_issue or not issue_matches(repository, after_issue) or not isinstance(after_comments, list) or any(not isinstance(comment, dict) or not valid_comment_shape(comment) for comment in after_comments):
            return result_emit("blocked", "blocked-unsafe", evidence, "post-comment verification is malformed")
        before_by_id = {comment["id"]: comment for comment in comments}
        after_by_id = {comment["id"]: comment for comment in after_comments}
        if any(after_by_id.get(identifier) != comment for identifier, comment in before_by_id.items()):
            return result_emit("blocked", "blocked-unsafe", evidence, "preexisting issue comments changed during mutation")
        new_comments = [comment for comment in after_comments if comment["id"] not in set(ids)]
        new_matches = [comment for comment in new_comments if exact_existing_match(comment, args.kind, body, actor, args.pr, args.head, args.attach, policy)]
        if len(new_matches) != 1 or len(new_comments) != 1:
            disposition = "waiting-external" if not new_comments else "blocked-unsafe"
            status = "waiting" if disposition == "waiting-external" else "blocked"
            return result_emit(status, disposition, evidence, posted.stderr.strip() or "authoritative comment reread did not prove one exact mutation")
        evidence["comment"] = new_matches[0]
        evidence["mutation_attribution"] = "certain" if posted.returncode == 0 else "uncertain"
        return result_emit("passed", "posted", evidence)
    finally:
        try:
            BODY_FILE.unlink(missing_ok=True)
        except OSError as exc:
            print(f"warning: could not remove {BODY_FILE}: {exc}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
