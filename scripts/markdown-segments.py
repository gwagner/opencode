#!/usr/bin/env python3
"""Emit NUL-delimited, context-preserving Markdown source segments."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ATX_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
SETEXT = re.compile(r"^\s{0,3}(=+|-+)\s*$")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
LIST_ITEM = re.compile(r"^\s{0,3}(?:[-+*]|\d+[.)])\s+")


def frontmatter_end(lines: list[str]) -> int:
    """Return the exclusive frontmatter boundary, or zero when absent."""
    if not lines or lines[0].strip() != "---":
        return 0
    for index in range(1, len(lines)):
        if lines[index].strip() in {"---", "..."}:
            return index + 1
    return 0


def structural_headings(
    lines: list[str], content_start: int
) -> dict[int, tuple[int, str]]:
    """Return heading line indexes, ignoring heading-like text in fences."""
    headings: dict[int, tuple[int, str]] = {}
    fence_marker: str | None = None
    for index in range(content_start, len(lines)):
        line = lines[index]
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(1)
            if fence_marker is None:
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                fence_marker = None
            continue
        if fence_marker is not None:
            continue
        match = ATX_HEADING.match(line)
        if match:
            headings[index] = (len(match.group(1)), match.group(2).strip())
            continue
        if index > content_start and SETEXT.match(line) and lines[index - 1].strip():
            level = 1 if line.lstrip().startswith("=") else 2
            headings[index - 1] = (level, lines[index - 1].strip())
    return headings


def safe_blocks(lines: list[str], start: int, end: int) -> list[tuple[int, int]]:
    """Split only at blank-line Markdown block boundaries outside fences."""
    blocks: list[tuple[int, int]] = []
    block_start = start
    fence_marker: str | None = None
    for index in range(start, end):
        fence = FENCE.match(lines[index])
        if fence:
            marker = fence.group(1)
            if fence_marker is None:
                fence_marker = marker[0]
            elif marker[0] == fence_marker:
                fence_marker = None
        loose_list_continues = False
        if not lines[index].strip():
            next_index = index + 1
            while next_index < end and not lines[next_index].strip():
                next_index += 1
            loose_list_continues = (
                any(LIST_ITEM.match(item) for item in lines[block_start:index])
                and next_index < end
                and LIST_ITEM.match(lines[next_index]) is not None
            )
        if (
            fence_marker is None
            and not lines[index].strip()
            and not loose_list_continues
            and index + 1 > block_start
        ):
            blocks.append((block_start, index + 1))
            block_start = index + 1
    if block_start < end:
        blocks.append((block_start, end))
    return blocks or [(start, end)]


def bounded_parts(
    lines: list[str], start: int, end: int, preferred_lines: int
) -> list[tuple[int, int]]:
    """Group intact Markdown blocks up to a preferred size."""
    if end - start <= preferred_lines:
        return [(start, end)]
    parts: list[tuple[int, int]] = []
    current_start: int | None = None
    current_end: int | None = None
    for block_start, block_end in safe_blocks(lines, start, end):
        if current_start is None:
            current_start, current_end = block_start, block_end
            continue
        assert current_end is not None
        if block_end - current_start <= preferred_lines:
            current_end = block_end
        else:
            parts.append((current_start, current_end))
            current_start, current_end = block_start, block_end
    assert current_start is not None and current_end is not None
    parts.append((current_start, current_end))
    return parts


def segments(
    lines: list[str], preferred_lines: int
) -> list[tuple[int, int, str, str]]:
    content_start = frontmatter_end(lines)
    if content_start >= len(lines):
        return []
    metadata_range = f"1-{content_start}" if content_start else "none"
    headings = structural_headings(lines, content_start)
    boundaries = sorted({content_start, *headings.keys(), len(lines)})
    hierarchy: list[str] = []
    result: list[tuple[int, int, str, str]] = []
    for boundary_index in range(len(boundaries) - 1):
        start, end = boundaries[boundary_index], boundaries[boundary_index + 1]
        if start == end:
            continue
        if start not in headings and not any(line.strip() for line in lines[start:end]):
            continue
        if start in headings:
            level, title = headings[start]
            hierarchy = hierarchy[: level - 1]
            hierarchy.append(title)
            context = " > ".join(hierarchy)
        else:
            context = "Document preamble"
        parts = bounded_parts(lines, start, end, preferred_lines)
        for part_index, (part_start, part_end) in enumerate(parts, start=1):
            part_context = context
            if len(parts) > 1:
                part_context = f"{context} [block group {part_index}/{len(parts)}]"
            result.append((part_start + 1, part_end, part_context, metadata_range))
    return result


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: markdown-segments.py <source.md> <preferred-lines>", file=sys.stderr)
        return 2
    source = Path(sys.argv[1])
    preferred_lines = int(sys.argv[2])
    if preferred_lines < 1:
        raise ValueError("preferred-lines must be positive")
    lines = source.read_text(encoding="utf-8").splitlines(keepends=True)
    for start, end, context, metadata_range in segments(lines, preferred_lines):
        for value in (str(start), str(end), context, metadata_range):
            sys.stdout.buffer.write(value.encode("utf-8") + b"\0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
