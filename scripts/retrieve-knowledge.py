#!/usr/bin/env python3
"""Search a Markdown knowledge bundle and return bounded section locators."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote


ATX_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
SETEXT = re.compile(r"^\s{0,3}(=+|-+)\s*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
LINK = re.compile(r"\[[^]]*\]\(([^)]+)\)")
WORD = re.compile(r"[\w-]+", re.UNICODE)
DEFAULT_MAX_SECTIONS = 10
EXCERPT_LIMIT = 280


@dataclass(frozen=True)
class Section:
    path: str
    line_start: int
    line_end: int
    heading: str
    body: str
    frontmatter: str


@dataclass(frozen=True)
class Result:
    path: str
    line_start: int
    line_end: int
    heading: str
    score: int
    excerpt: str


def frontmatter_end(lines: list[str]) -> int:
    """Return the exclusive YAML frontmatter boundary, or zero."""
    if not lines or lines[0].strip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].strip() in {"---", "..."}:
            return index + 1
    return 0


def structural_headings(
    lines: list[str], content_start: int
) -> dict[int, tuple[int, str]]:
    """Find ATX and Setext headings while ignoring fenced content."""
    headings: dict[int, tuple[int, str]] = {}
    fence_marker: str | None = None
    for index in range(content_start, len(lines)):
        fence = FENCE.match(lines[index])
        if fence:
            marker = fence.group(1)[0]
            fence_marker = marker if fence_marker is None else None if marker == fence_marker else fence_marker
            continue
        if fence_marker is not None:
            continue
        match = ATX_HEADING.match(lines[index])
        if match:
            headings[index] = (len(match.group(1)), match.group(2).strip())
        elif index > content_start and SETEXT.match(lines[index]) and lines[index - 1].strip():
            level = 1 if lines[index].lstrip().startswith("=") else 2
            headings[index - 1] = (level, lines[index - 1].strip())
    return headings


def document_sections(path: Path, root: Path) -> list[Section]:
    lines = path.read_text(encoding="utf-8").splitlines()
    metadata_end = frontmatter_end(lines)
    frontmatter = "\n".join(lines[:metadata_end])
    headings = structural_headings(lines, metadata_end)
    boundaries = sorted({metadata_end, *headings.keys(), len(lines)})
    hierarchy: list[str] = []
    sections: list[Section] = []
    relative = path.relative_to(root).as_posix()
    for index in range(len(boundaries) - 1):
        start, end = boundaries[index], boundaries[index + 1]
        if start == end or not any(line.strip() for line in lines[start:end]):
            continue
        if start in headings:
            level, title = headings[start]
            hierarchy = hierarchy[: level - 1]
            hierarchy.append(title)
            heading = " > ".join(hierarchy)
        else:
            heading = "Document preamble"
        sections.append(
            Section(relative, start + 1, end, heading, "\n".join(lines[start:end]), frontmatter)
        )
    if not sections and frontmatter:
        sections.append(Section(relative, 1, metadata_end, "Document metadata", "", frontmatter))
    return sections


def markdown_files(root: Path) -> tuple[list[Path], list[Path]]:
    content: list[Path] = []
    indexes: list[Path] = []
    for path in sorted(root.rglob("*.md"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root)
        if ".reorganization" in relative.parts or not path.is_file():
            continue
        if path.name.lower() == "index.md":
            indexes.append(path)
        elif path.name.lower() != "log.md":
            content.append(path)
    return content, indexes


def occurrences(text: str, phrase: str, terms: tuple[str, ...]) -> int:
    folded = text.casefold()
    score = sum(1 for term in terms if term in folded)
    if len(terms) > 1 and phrase in folded:
        score += len(terms)
    return score


def navigation_scores(
    indexes: list[Path], root: Path, phrase: str, terms: tuple[str, ...]
) -> dict[str, int]:
    scores: dict[str, int] = {}
    for index in indexes:
        for line in index.read_text(encoding="utf-8").splitlines():
            relevance = occurrences(line, phrase, terms)
            if not relevance:
                continue
            for raw_target in LINK.findall(line):
                target = unquote(raw_target.split("#", 1)[0].strip().split(maxsplit=1)[0])
                if not target or "://" in target or target.startswith(("#", "/")):
                    continue
                resolved = (index.parent / target).resolve()
                try:
                    relative = resolved.relative_to(root).as_posix()
                except ValueError:
                    continue
                if relative.lower().endswith(".md"):
                    scores[relative] = scores.get(relative, 0) + 50 * relevance
    return scores


def excerpt(body: str, terms: tuple[str, ...]) -> str:
    lines = [re.sub(r"\s+", " ", line).strip() for line in body.splitlines() if line.strip()]
    if not lines:
        return ""
    match_index = next(
        (index for index, line in enumerate(lines) if any(term in line.casefold() for term in terms)),
        0,
    )
    text = " ".join(lines[max(0, match_index - 1) : match_index + 2])
    if len(text) <= EXCERPT_LIMIT:
        return text
    return text[: EXCERPT_LIMIT - 1].rstrip() + "…"


def retrieve(root: Path, query: str, limit: int) -> list[Result]:
    phrase = query.casefold().strip()
    terms = tuple(dict.fromkeys(match.group(0).casefold() for match in WORD.finditer(query)))
    if not terms:
        raise ValueError("query must contain a searchable word")
    content, indexes = markdown_files(root)
    nav_scores = navigation_scores(indexes, root, phrase, terms)
    results: list[Result] = []
    for path in content:
        for section in document_sections(path, root):
            score = nav_scores.get(section.path, 0)
            score += 40 * occurrences(section.path, phrase, terms)
            score += 30 * occurrences(section.frontmatter, phrase, terms)
            score += 20 * occurrences(section.heading, phrase, terms)
            score += 10 * occurrences(section.body, phrase, terms)
            if score:
                results.append(
                    Result(
                        section.path,
                        section.line_start,
                        section.line_end,
                        section.heading,
                        score,
                        excerpt(section.body or section.frontmatter, terms),
                    )
                )
    results.sort(key=lambda item: (-item.score, item.path, item.line_start, item.line_end))
    return results[:limit]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="knowledge bundle root")
    parser.add_argument("--max-sections", type=int, default=DEFAULT_MAX_SECTIONS)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("query", nargs="+", help="search terms")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        root = args.root.expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError("root must be a directory")
        if args.max_sections < 1:
            raise ValueError("max-sections must be positive")
        results = retrieve(root, " ".join(args.query), args.max_sections)
    except (OSError, UnicodeError, ValueError) as error:
        print(f"retrieve-knowledge.py: {error}", file=sys.stderr)
        return 2

    if args.as_json:
        json.dump([asdict(result) for result in results], sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        for result in results:
            print(
                f"{result.path}:{result.line_start}-{result.line_end} "
                f"[{result.heading}] score={result.score}"
            )
            if result.excerpt:
                print(f"  {result.excerpt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
