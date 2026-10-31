#!/usr/bin/env python3
"""Validate deterministic agent/skill definitions and their direct contracts."""
from __future__ import annotations

import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NATIVE_PERMISSION_KEYS = {
    "*",
    "read",
    "edit",
    "glob",
    "grep",
    "bash",
    "task",
    "todowrite",
    "skill",
    "lsp",
    "question",
    "webfetch",
    "websearch",
    "external_directory",
    "doom_loop",
}
PERMISSION_ACTIONS = {"allow", "ask", "deny"}
AGENT_MODES = {"all", "primary", "subagent"}

import yaml


@dataclass(frozen=True)
class Definition:
    path: Path
    kind: str
    name: str
    data: dict[str, Any]
    text: str


def fail(path: Path, message: str) -> AssertionError:
    return AssertionError(f"{path}: {message}")


def frontmatter(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise fail(path, "missing YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise fail(path, "missing YAML frontmatter terminator")
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as error:
        raise fail(path, f"invalid YAML frontmatter: {error}") from error
    if not isinstance(data, dict):
        raise fail(path, "frontmatter must be a mapping")
    return data, text


def yaml_block_style(path: Path, label: str, source: str) -> list[str]:
    """Return flow-style collection findings and surface YAML parse failures."""
    findings: list[str] = []
    try:
        documents = list(yaml.compose_all(source))
    except yaml.YAMLError as error:
        return [f"{label}: invalid YAML: {error}"]

    def walk(node: yaml.Node | None) -> None:
        if node is None:
            return
        if isinstance(node, (yaml.MappingNode, yaml.SequenceNode)):
            if node.value and node.flow_style:
                findings.append(f"{label}:{node.start_mark.line + 1}: flow-style collection")
            for child in node.value:
                if isinstance(node, yaml.MappingNode):
                    walk(child[0])
                    walk(child[1])
                else:
                    walk(child)

    for document in documents:
        walk(document)
    return findings


def local_markdown_links(root: Path, path: Path, text: str) -> list[str]:
    findings: list[str] = []
    for raw_target in re.findall(r"(?<!\!)\[[^]]*\]\(([^)]+)\)", text):
        target = raw_target.strip()
        if target.startswith("<") and ">" in target:
            target = target[1 : target.index(">")]
        else:
            target = target.split(" ", 1)[0]
        target = target.split("#", 1)[0]
        if not target or target.startswith(("/", "http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).resolve().is_file():
            findings.append(f"broken Markdown link {target}")
    return findings


def yaml_workflows(path: Path, text: str) -> tuple[list[dict[str, Any]], list[str]]:
    workflows: list[dict[str, Any]] = []
    findings: list[str] = []
    for index, block in enumerate(re.findall(r"```yaml\n(.*?)\n```", text, re.S), start=1):
        findings.extend(yaml_block_style(path, f"YAML block {index}", block))
        try:
            document = yaml.safe_load(block)
        except yaml.YAMLError:
            continue
        if not isinstance(document, dict) or not isinstance(document.get("workflow"), list):
            continue
        # Canonical documentation examples use angle-bracket placeholders and are not workflow edges.
        if "<" in str(document.get("request", "")):
            continue
        workflows.append(document)
    return workflows, findings


def inputs_section(text: str) -> str | None:
    match = re.search(r"^## Inputs\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def declares_caller_provided_permitted_paths(value: Any) -> bool:
    """Whether an input declaration makes the caller the path restrictor."""
    if isinstance(value, str):
        return bool(
            re.search(
                r"\bcaller-provided\b.*\bpermitted\b.*\bpaths?\b",
                value,
                re.I | re.S,
            )
        )
    if isinstance(value, list):
        return any(declares_caller_provided_permitted_paths(item) for item in value)
    return False


def workflow_edges(workflow: list[Any]) -> list[tuple[str, str]]:
    edges: list[tuple[str, str]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                if key in {"skill", "agent"} and isinstance(child, str):
                    edges.append((key, child))
                else:
                    walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(workflow)
    return edges


def permission_findings(permission: Any) -> list[str]:
    """Validate the native OpenCode permission schema."""
    if isinstance(permission, str):
        return [] if permission in PERMISSION_ACTIONS else ["permission scalar must be allow, ask, or deny"]
    if not isinstance(permission, dict):
        return ["permission must be an allow, ask, deny scalar or a mapping"]

    findings: list[str] = []
    for permission_name, rule in permission.items():
        if permission_name not in NATIVE_PERMISSION_KEYS:
            findings.append(f"invalid native permission key {permission_name!r}")
        if isinstance(rule, str):
            if rule not in PERMISSION_ACTIONS:
                findings.append(f"{permission_name}: action must be allow, ask, or deny")
        elif isinstance(rule, dict):
            for pattern, action in rule.items():
                if not isinstance(pattern, str) or not isinstance(action, str) or action not in PERMISSION_ACTIONS:
                    findings.append(f"{permission_name}: pattern-map actions must be allow, ask, or deny")
        else:
            findings.append(f"{permission_name}: rule must be an action or pattern map")
    return findings


def permission_rules(permission: Any) -> list[tuple[str, str, str]]:
    """Normalize native permission maps without reordering their rules."""
    if isinstance(permission, str):
        return [("*", "*", permission)] if permission in PERMISSION_ACTIONS else []
    if not isinstance(permission, dict):
        return []
    rules: list[tuple[str, str, str]] = []
    for action, value in permission.items():
        if isinstance(value, str) and value in PERMISSION_ACTIONS:
            rules.append((action, "*", value))
        elif isinstance(value, dict):
            for resource, effect in value.items():
                if isinstance(resource, str) and effect in PERMISSION_ACTIONS:
                    rules.append((action, resource, effect))
    return rules


def matches(pattern: str, value: str) -> bool:
    """Match OpenCode's whole-value wildcard semantics."""
    normalized = value.replace("\\", "/")
    normalized_pattern = pattern.replace("\\", "/")
    expression = "".join(
        ".*" if character == "*" else "." if character == "?" else re.escape(character)
        for character in normalized_pattern
    )
    if expression.endswith(r"\ \.\*"):
        expression = expression[:-6] + r"(?:\ .*)?"
    return re.fullmatch(expression, normalized, flags=re.DOTALL) is not None


def permission_effect(permission: Any, action: str, resource: str) -> str:
    """Return the last matching OpenCode permission effect, or its ask default."""
    effect = "ask"
    for rule_action, rule_resource, rule_effect in permission_rules(permission):
        if matches(rule_action, action) and matches(rule_resource, resource):
            effect = rule_effect
    return effect


def fixed_absolute_bash_paths(permission: dict[str, Any]) -> list[str]:
    """Return literal absolute paths used by allowed bash command patterns."""
    bash = permission.get("bash")
    if not isinstance(bash, dict):
        return []
    paths: list[str] = []
    for command, action in bash.items():
        if action != "allow" or not isinstance(command, str):
            continue
        try:
            tokens = shlex.split(command)
        except ValueError:
            continue
        paths.extend(token for token in tokens if token.startswith("/"))
    return paths


def external_path_is_covered(permission: dict[str, Any], path: str) -> bool:
    external = permission.get("external_directory")
    return isinstance(external, dict) and external.get(path) == "allow"


def covers(actual: Any, required: Any) -> bool:
    """Whether every fixed contract rule resolves to its exact required effect."""
    # Legacy scalar contracts describe caller-provided paths. They deliberately
    # cannot name a static resource to evaluate; retain their historical
    # compatibility rule while fixed pattern contracts use exact ordered evaluation.
    if isinstance(required, dict):
        for action, effect in required.items():
            if isinstance(effect, str) and effect in PERMISSION_ACTIONS:
                if not any(
                    rule_action == action and rule_effect == effect
                    for rule_action, _resource, rule_effect in permission_rules(actual)
                ):
                    return False
        required_rules = [
            rule
            for action, value in required.items()
            if isinstance(value, dict)
            for rule in permission_rules({action: value})
        ]
    else:
        required_rules = permission_rules(required)
    return all(
        permission_effect(actual, action, resource) == effect
        for action, resource, effect in required_rules
    )


def permission_for(definition: Definition) -> Any:
    """Select the agent runtime permission or skill minimum contract."""
    return definition.data.get("permission" if definition.kind == "agent" else "opencode_permission", {}) or {}


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    paths = sorted((root / "agents").glob("*.md")) + sorted((root / "skills").glob("*/SKILL.md"))
    definitions: dict[tuple[str, str], Definition] = {}
    findings: list[str] = []
    edges: dict[tuple[str, str], list[tuple[str, str]]] = {}

    for path in paths:
        try:
            data, text = frontmatter(path)
        except AssertionError as error:
            findings.append(str(error))
            continue
        kind = "agent" if path.parent == root / "agents" else "skill"
        expected_name = path.stem if kind == "agent" else path.parent.name
        name = data.get("name")
        if name != expected_name:
            findings.append(f"{path.relative_to(root)}: name must be {expected_name!r}, got {name!r}")
        if data.get("classification") not in {"technical", "non-technical"}:
            findings.append(f"{path.relative_to(root)}: classification must be technical or non-technical")
        key = (kind, expected_name)
        if key in definitions:
            findings.append(f"{path.relative_to(root)}: duplicate {kind} identity {expected_name}")
        definitions[key] = Definition(path, kind, expected_name, data, text)
        findings.extend(f"{path.relative_to(root)}: {item}" for item in local_markdown_links(root, path, text))
        frontmatter_source = text.split("---\n", 2)[1]
        findings.extend(f"{path.relative_to(root)}: {item}" for item in yaml_block_style(path, "frontmatter", frontmatter_source))
        if kind == "skill":
            contract = data.get("opencode_permission") or {}
            if isinstance(contract, dict) and any(
                contract.get(name) == "allow" for name in ("read", "edit")
            ):
                if not declares_caller_provided_permitted_paths(data.get("inputs")):
                    findings.append(
                        f"{path.relative_to(root)}: scalar read or edit permission requires an inputs frontmatter entry "
                        "declaring caller-provided permitted paths"
                    )
                body_inputs = inputs_section(text)
                if not body_inputs or not declares_caller_provided_permitted_paths(body_inputs):
                    findings.append(
                        f"{path.relative_to(root)}: scalar read or edit permission requires ## Inputs wording "
                        "declaring caller-provided permitted paths"
                    )
        elif data.get("mode", "all") not in AGENT_MODES:
            findings.append(
                f"{path.relative_to(root)}: mode must be all, primary, or subagent"
            )

    for key, definition in definitions.items():
        workflows, workflow_findings = yaml_workflows(definition.path, definition.text)
        findings.extend(f"{definition.path.relative_to(root)}: {item}" for item in workflow_findings)
        edges[key] = []
        permission = permission_for(definition)
        permission_errors = permission_findings(permission)
        findings.extend(f"{definition.path.relative_to(root)}: {item}" for item in permission_errors)
        if not isinstance(permission, dict):
            continue
        for fixed_path in fixed_absolute_bash_paths(permission):
            if not external_path_is_covered(permission, fixed_path):
                findings.append(
                    f"{definition.path.relative_to(root)}: bash fixed external path {fixed_path} "
                    "lacks exact external_directory permission coverage"
                )
        for workflow in workflows:
            for edge_kind, target in workflow_edges(workflow["workflow"]):
                target_key = (edge_kind, target)
                if target_key not in definitions:
                    findings.append(f"{definition.path.relative_to(root)}: unresolved {edge_kind} {target}")
                    continue
                edges[key].append(target_key)
                grant_key = "skill" if edge_kind == "skill" else "task"
                if permission_effect(permission, grant_key, target) != "allow":
                    findings.append(f"{definition.path.relative_to(root)}: missing {grant_key} allow permission for {target}")
                if edge_kind == "skill":
                    contract = permission_for(definitions[target_key])
                    if not isinstance(contract, dict):
                        findings.append(f"{definition.path.relative_to(root)} -> {target}: invalid opencode_permission")
                        continue
                    if not covers(permission, contract):
                        for action, resource, effect in permission_rules(contract):
                            if permission_effect(permission, action, resource) != effect:
                                findings.append(
                                    f"{definition.path.relative_to(root)} -> {target}: missing {action} {effect} permission coverage for {resource}"
                                )

    # Direct self-delegation and indirect recursive edges are unsafe.
    visiting: set[tuple[str, str]] = set()
    visited: set[tuple[str, str]] = set()

    def visit(node: tuple[str, str], trail: list[tuple[str, str]]) -> None:
        if node in visiting:
            cycle = trail[trail.index(node) :] + [node]
            findings.append("recursive workflow cycle: " + " -> ".join(name for _, name in cycle))
            return
        if node in visited:
            return
        visiting.add(node)
        for child in edges.get(node, []):
            visit(child, trail + [child])
        visiting.remove(node)
        visited.add(node)

    for key in definitions:
        visit(key, [key])

    reachable: set[tuple[str, str]] = set()

    def reach(node: tuple[str, str]) -> None:
        if node in reachable:
            return
        reachable.add(node)
        for child in edges.get(node, []):
            reach(child)

    for key in definitions:
        if key[0] == "agent":
            reach(key)
    for key, definition in definitions.items():
        if key[0] == "skill" and key not in reachable:
            findings.append(f"{definition.path.relative_to(root)}: orphan skill")

    if findings:
        raise AssertionError("\n".join(findings))
    edge_count = sum(len(value) for value in edges.values())
    print(f"agent-skill architecture passed: {len(definitions)} definitions, {edge_count} workflow edges")


if __name__ == "__main__":
    main()
