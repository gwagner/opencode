#!/usr/bin/env python3
"""Report dangling repository agent, skill, and architecture-test references."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CATALOG_HEADING = re.compile(r"^## (Agents|Skills)\s*$")
CATALOG_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|")
LOOP = re.compile(r"^\s*for\s+(\w+)\s+in\s+(.+?);\s*do\s*$")


def diagnostic(path: Path, line: int, message: str, root: Path) -> None:
    try:
        display = path.relative_to(root)
    except ValueError:
        display = path
    print(f"{display}:{line}: {message}", file=sys.stderr)


def canonical_assets(root: Path) -> tuple[set[str], set[str]]:
    agents = {path.stem for path in (root / "agents").glob("*.md")}
    skills = {
        path.parent.name for path in (root / "skills").glob("*/SKILL.md")
    }
    return agents, skills


def audit_readme(root: Path, agents: set[str], skills: set[str]) -> int:
    path = root / "README.md"
    errors = 0
    section: str | None = None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        heading = CATALOG_HEADING.match(line)
        if heading:
            section = heading.group(1)
            continue
        if line.startswith("## "):
            section = None
        if section is None:
            continue
        row = CATALOG_ROW.match(line)
        if not row:
            continue
        name = row.group(1).strip(" `")
        if name in {"Agent", "Skill", "---"}:
            continue
        known = agents if section == "Agents" else skills
        kind = section[:-1].lower()
        if name not in known:
            diagnostic(path, number, f"dangling {kind} reference '{name}'", root)
            errors += 1
    return errors


def loop_references(lines: list[str], start: int, variable: str) -> str | None:
    body: list[str] = []
    for line in lines[start + 1 :]:
        if re.match(r"^\s*done\s*$", line):
            break
        body.append(line)
    joined = "\n".join(body)
    if re.search(rf"/agents/\${{{variable}}}\.md|/agents/\${variable}\.md", joined):
        return "agent"
    if re.search(rf"/skills/\${{{variable}}}(?:/|\b)|/skills/\${variable}(?:/|\b)", joined):
        return "skill"
    return None


def audit_architecture_test(root: Path, agents: set[str], skills: set[str]) -> int:
    path = root / "tests" / "agent-skill-architecture.sh"
    lines = path.read_text(encoding="utf-8").splitlines()
    errors = 0

    for index, line in enumerate(lines):
        number = index + 1
        negative_existence_check = bool(re.search(r"\btest\s+!\s+-[ef]\b", line))
        loop = LOOP.match(line)
        if loop:
            kind = loop_references(lines, index, loop.group(1))
            if kind:
                known = agents if kind == "agent" else skills
                for name in loop.group(2).split():
                    if name not in known:
                        diagnostic(path, number, f"dangling {kind} reference '{name}'", root)
                        errors += 1

        if not negative_existence_check:
            for name in re.findall(r"(?:/code|\$root|\$\{root\})/agents/([a-z0-9-]+)\.md", line):
                if name not in agents:
                    diagnostic(path, number, f"dangling agent reference '{name}'", root)
                    errors += 1
            for name in re.findall(r"(?:/code|\$root|\$\{root\})/skills/([a-z0-9-]+)", line):
                if name not in skills:
                    diagnostic(path, number, f"dangling skill reference '{name}'", root)
                    errors += 1

        if negative_existence_check:
            continue
        for relative in re.findall(r"(?:\$root|\$\{root\})/([^\"'\s;]+)", line):
            if "$" in relative or "*" in relative:
                continue
            if not (root / relative).exists():
                diagnostic(
                    path,
                    number,
                    f"dangling checked /code asset reference '/code/{relative}'",
                    root,
                )
                errors += 1
    return errors


def main() -> int:
    default_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=default_root)
    args = parser.parse_args()
    root = args.root.resolve()

    agents, skills = canonical_assets(root)
    errors = audit_readme(root, agents, skills)
    errors += audit_architecture_test(root, agents, skills)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
