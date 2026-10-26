#!/usr/bin/env python3
"""Validate local Markdown links and direct skill permission contracts."""
from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path

import yaml


def frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise AssertionError(f"{path}: missing YAML frontmatter")
    data = yaml.safe_load(parts[1])
    if not isinstance(data, dict):
        raise AssertionError(f"{path}: frontmatter must be a mapping")
    return data, text


def local_markdown_links(root: Path, path: Path, text: str) -> None:
    for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", text):
        target = target.split("#", 1)[0].split(" ", 1)[0]
        if not target or target.startswith(("/", "http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).resolve().is_file():
            raise AssertionError(f"{path.relative_to(root)}: broken Markdown link {target}")


def workflow_skill_edges(text: str) -> list[str]:
    targets = []
    for block in re.findall(r"```yaml\n(.*?)\n```", text, re.S):
        document = yaml.safe_load(block)
        if not isinstance(document, dict) or not isinstance(document.get("workflow"), list):
            continue
        if "<" in str(document.get("request", "")):
            continue

        def walk(value: object) -> None:
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "skill" and isinstance(child, str):
                        targets.append(child)
                    else:
                        walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        walk(document["workflow"])
    return targets


def covers(actual: object, required: object) -> bool:
    if actual == "allow":
        return True
    if required == "allow":
        return isinstance(actual, dict) and any(value == "allow" for value in actual.values())
    if not isinstance(required, dict) or not isinstance(actual, dict):
        return False
    return all(
        action != "allow" or any(
            granted == "allow" and fnmatch.fnmatchcase(pattern, allowed_pattern)
            for allowed_pattern, granted in actual.items()
        )
        for pattern, action in required.items()
    )


def main() -> None:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    definitions = sorted((root / "agents").glob("*.md")) + sorted((root / "skills").glob("*/SKILL.md"))
    skills = {}
    callers = []
    for path in definitions:
        data, text = frontmatter(path)
        local_markdown_links(root, path, text)
        if path.parent.parent.name == "skills":
            skills[path.parent.name] = data
        callers.append((path, data, text))

    edge_count = 0
    failures = []
    for path, data, text in callers:
        permission = data.get("permission" if path.parent.name == "agents" else "opencode_permission", {}) or {}
        for skill_name in workflow_skill_edges(text):
            skill = skills.get(skill_name)
            if skill is None:
                failures.append(f"{path}: unresolved skill {skill_name}")
                continue
            if not covers(permission.get("skill"), {skill_name: "allow"}):
                failures.append(f"{path}: missing skill permission for {skill_name}")
            for name, requirement in (skill.get("opencode_permission") or {}).items():
                if not covers(permission.get(name), requirement):
                    failures.append(f"{path} -> {skill_name}: missing {name} permission coverage")
            edge_count += 1
    if failures:
        raise AssertionError("\n".join(failures))
    print(f"agent-skill contracts passed: {edge_count} direct skill edges")


if __name__ == "__main__":
    main()
