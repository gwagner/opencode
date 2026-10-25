#!/usr/bin/env python3
"""Validate deterministic agent and skill architecture invariants."""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

import yaml


PLACEHOLDER_REQUESTS = {
    "One deterministic technical agent or skill.",
}
PERMISSION_VALIDATION_ROOTS = {
    "agent-builder",
    "sdlc-orchestrator",
}
DIRECT_PERMISSION_SOURCES = {
    "github-issue-manager",
    "github-pr-approved-merge",
    "github-pr-user-decision",
    "issue-worktree-validation",
}
FORBIDDEN_CONTRACT_KEYS = {
    "authoritative",
    "call",
    "callers",
    "source",
    "status",
}
PERMISSION_ACTIONS = {
    "allow",
    "ask",
    "deny",
}


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise AssertionError(f"{path}: missing YAML frontmatter")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise AssertionError(f"{path}: frontmatter is not a mapping")
    return data, text


def workflow_edges(text: str) -> list[tuple[str, str]]:
    edges = []
    for match in re.finditer(r"```yaml\n(.*?)\n```", text, re.S):
        block = yaml.safe_load(match.group(1))
        if not isinstance(block, dict) or "workflow" not in block:
            continue
        request = str(block.get("request", ""))
        if "<" in request or request in PLACEHOLDER_REQUESTS:
            continue

        def walk(value: object) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"skill", "agent"} and isinstance(child, str):
                        edges.append((key, child))
                    else:
                        walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(block["workflow"])
    return edges


def has_allow(value: object) -> bool:
    return value == "allow" or isinstance(value, dict) and any(action == "allow" for action in value.values())


def pattern_covered(value: object, required: str) -> bool:
    if value == "allow":
        return True
    return isinstance(value, dict) and any(
        action == "allow" and (pattern == required or fnmatch.fnmatchcase(required, pattern))
        for pattern, action in value.items()
    )


def validate_contract_coverage(caller: dict, skill: dict, edge: str) -> None:
    permissions = caller["data"].get("permission" if caller["kind"] == "agent" else "opencode_permission", {}) or {}
    contract = skill["data"].get("opencode_permission", {}) or {}
    for permission_name, requirement in contract.items():
        if permission_name == "skill":
            continue
        actual = permissions.get(permission_name)
        if requirement == "allow":
            covered = has_allow(actual) if permission_name in {"read", "edit"} else actual == "allow"
            if not covered:
                raise AssertionError(f"{edge}: missing scalar {permission_name}: allow coverage")
        elif isinstance(requirement, dict):
            for pattern, action in requirement.items():
                if action == "allow" and not pattern_covered(actual, pattern):
                    raise AssertionError(f"{edge}: missing {permission_name} coverage for {pattern}")


def validate_yaml_style(path: Path, text: str) -> None:
    in_frontmatter = False
    in_yaml = False
    delimiters = 0
    for number, line in enumerate(text.splitlines(), 1):
        if line == "---" and delimiters < 2:
            delimiters += 1
            in_frontmatter = delimiters == 1
            continue
        if line == "```yaml":
            in_yaml = True
            continue
        if line == "```" and in_yaml:
            in_yaml = False
            continue
        if (in_frontmatter or in_yaml) and re.search(r":\s*\[[^\]]+\]|:\s*\{[^}]+\}", line):
            raise AssertionError(f"{path}:{number}: flow-style YAML collection")


def validate_markdown_links(root: Path, path: Path, text: str) -> None:
    for match in re.finditer(r"\[[^\]]*\]\(([^)]+\.md)(?:#[^)]+)?\)", text):
        target = match.group(1)
        if target.startswith(("/", "http://", "https://")):
            continue
        if not (path.parent / target).resolve().exists():
            raise AssertionError(f"{path.relative_to(root)}: broken Markdown link {target}")


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parents[1]
    paths = sorted((root / "agents").glob("*.md")) + sorted((root / "skills").glob("*/SKILL.md"))
    objects: dict[str, dict] = {}

    for path in paths:
        data, text = frontmatter(path)
        kind = "agent" if path.parent.name == "agents" else "skill"
        expected = path.stem if kind == "agent" else path.parent.name
        if data.get("name") != expected:
            raise AssertionError(f"{path}: identity {data.get('name')!r} does not match {expected!r}")
        if data.get("classification") not in {"technical", "non-technical"}:
            raise AssertionError(f"{path}: invalid classification")
        if expected in objects:
            raise AssertionError(f"duplicate identity: {expected}")
        if kind == "skill":
            contract = data.get("opencode_permission")
            if not isinstance(contract, dict):
                raise AssertionError(f"{path}: missing opencode_permission mapping")
            if FORBIDDEN_CONTRACT_KEYS.intersection(contract):
                raise AssertionError(f"{path}: trace-only permission key")
            for permission_name, rule in contract.items():
                if isinstance(rule, str):
                    if rule not in PERMISSION_ACTIONS:
                        raise AssertionError(f"{path}: invalid action for {permission_name}")
                elif isinstance(rule, dict):
                    if any(action not in PERMISSION_ACTIONS for action in rule.values()):
                        raise AssertionError(f"{path}: invalid mapped action for {permission_name}")
                else:
                    raise AssertionError(f"{path}: invalid permission rule for {permission_name}")
            if not isinstance(data.get("inputs"), list) or not data["inputs"]:
                raise AssertionError(f"{path}: missing frontmatter inputs")
            if "## Inputs" not in text:
                raise AssertionError(f"{path}: missing body Inputs section")
        validate_yaml_style(path, text)
        validate_markdown_links(root, path, text)
        objects[expected] = {"path": path, "data": data, "text": text, "kind": kind}

    graph = {name: [] for name in objects}
    incoming = {name: 0 for name in objects}
    direct_edges: list[tuple[str, str, str]] = []
    for name, obj in objects.items():
        permissions = obj["data"].get("permission" if obj["kind"] == "agent" else "opencode_permission", {}) or {}
        for target_kind, target in workflow_edges(obj["text"]):
            if target not in objects or objects[target]["kind"] != target_kind:
                raise AssertionError(f"{obj['path']}: unresolved {target_kind} edge {target}")
            permission_name = "task" if target_kind == "agent" else "skill"
            grant = permissions.get(permission_name)
            if not (grant == "allow" or isinstance(grant, dict) and grant.get(target) == "allow"):
                raise AssertionError(f"{obj['path']}: missing {permission_name} permission for {target}")
            graph[name].append(target)
            incoming[target] += 1
            direct_edges.append((name, target_kind, target))

    active: list[str] = []
    visited: set[str] = set()

    def visit(name: str) -> None:
        if name in active:
            raise AssertionError("workflow cycle: " + " -> ".join(active + [name]))
        if name in visited:
            return
        active.append(name)
        for target in graph[name]:
            visit(target)
        active.pop()
        visited.add(name)

    for name in graph:
        visit(name)

    permission_edge_count = 0
    for source, kind, target in direct_edges:
        if source in DIRECT_PERMISSION_SOURCES and kind == "skill":
            validate_contract_coverage(objects[source], objects[target], f"{source} -> {target}")
            permission_edge_count += 1

    for root_name in sorted(PERMISSION_VALIDATION_ROOTS):
        root_object = objects.get(root_name)
        if not root_object or root_object["kind"] != "agent":
            raise AssertionError(f"permission validation root is not an agent: {root_name}")
        skill_closure: set[str] = set()
        pending = [target for source, kind, target in direct_edges if source == root_name and kind == "skill"]
        while pending:
            skill_name = pending.pop()
            if skill_name in skill_closure:
                continue
            skill_closure.add(skill_name)
            pending.extend(
                target
                for source, kind, target in direct_edges
                if source == skill_name and kind == "skill"
            )

        root_skill_grants = root_object["data"].get("permission", {}).get("skill")
        for skill_name in sorted(skill_closure):
            if not (root_skill_grants == "allow" or isinstance(root_skill_grants, dict) and root_skill_grants.get(skill_name) == "allow"):
                raise AssertionError(f"{root_name}: missing transitive skill permission for {skill_name}")
            validate_contract_coverage(root_object, objects[skill_name], f"{root_name} runtime -> {skill_name}")
            permission_edge_count += 1

        closure_sources = skill_closure | {root_name}
        for source, kind, target in direct_edges:
            if source in closure_sources and kind == "skill":
                validate_contract_coverage(objects[source], objects[target], f"{source} -> {target}")
                permission_edge_count += 1
    orphans = [name for name, obj in objects.items() if obj["kind"] == "skill" and incoming[name] == 0]
    if orphans:
        raise AssertionError("unreferenced skills: " + ", ".join(sorted(orphans)))

    readme = (root / "README.md").read_text()
    skill_section = readme.split("## Skills\n", 1)[1].split("## Graphify\n", 1)[0]
    agent_section = readme.split("## Agents\n", 1)[1].split("## Skills\n", 1)[0]
    rows = {}
    for section in (agent_section, skill_section):
        for line in section.splitlines():
            match = re.fullmatch(r"\| ([^|]+) \| (.+) \|", line)
            if match and match.group(1) not in {"Agent", "Skill", "---"}:
                rows[match.group(1)] = match.group(2)
    expected_rows = {name: obj["data"]["description"] for name, obj in objects.items()}
    if rows != expected_rows:
        missing = sorted(set(expected_rows) - set(rows))
        extra = sorted(set(rows) - set(expected_rows))
        changed = sorted(name for name in set(rows).intersection(expected_rows) if rows[name] != expected_rows[name])
        raise AssertionError(f"README inventory mismatch; missing={missing}, extra={extra}, changed={changed}")

    forbidden = [
        root / "agents/github-sdlc.md",
        root / "agents/merge-evidence-resolver.md",
        root / "skills/evidence-based-merge-resolution/SKILL.md",
        root / "skills/git-agent-skill-change-publication/SKILL.md",
        root / "skills/git-main-sync/SKILL.md",
    ]
    if any(path.exists() for path in forbidden):
        raise AssertionError("removed architecture file reappeared")
    obsolete = re.compile(r"agent: github-sdlc|execution_route: github-sdlc|`github-sdlc`")
    if any(obsolete.search(obj["text"]) for obj in objects.values()):
        raise AssertionError("obsolete github-sdlc routing remains")

    agent_count = sum(obj["kind"] == "agent" for obj in objects.values())
    skill_count = sum(obj["kind"] == "skill" for obj in objects.values())
    edge_count = sum(len(targets) for targets in graph.values())
    print(f"architecture graph passed: {agent_count} agents, {skill_count} skills, {edge_count} edges, {permission_edge_count} permission checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
