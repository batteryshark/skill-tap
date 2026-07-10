#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Find work-product prose that deserves human review.

This is a candidate scanner, not a linter. It deliberately over-reports phrases
that often indicate internal reasoning, defensive explanation, or AI-shaped
meta commentary in public documentation.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

TEXT_EXTS = {
    ".md",
    ".mdx",
    ".rst",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".css",
    ".go",
    ".html",
    ".java",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
}

SKIP_PARTS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".ruff_cache",
    ".internal",
    ".agent-work",
}

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (
        "defensive-objection",
        re.compile(
            r"\b(not just|not merely|not only|not a replacement|not meant to|"
            r"not the whole|not the entire|not an? (?:accusation|guarantee|oracle|verdict)|"
            r"does not mean|do not assume|is not intended)\b",
            re.I,
        ),
    ),
    (
        "meta-thesis",
        re.compile(
            r"\b(the thesis is|the point is|the goal is not|the real question|"
            r"what really matters|at its core|the deeper issue|the heart of)\b",
            re.I,
        ),
    ),
    (
        "internal-reasoning",
        re.compile(
            r"\b(why this exists|we chose|we decided|the intent is|the work is|"
            r"this means|this is useful because|former(?:ly)?|previous(?:ly)?|"
            r"backlog|handoff|task[- ]?id|T-\d{3}|board)\b",
            re.I,
        ),
    ),
    (
        "assurance-claim",
        re.compile(
            r"\b(measured, not asserted|claims are|regression[- ]gated|"
            r"production[- ]ready|safe by default|battle[- ]tested|enterprise[- ]ready)\b",
            re.I,
        ),
    ),
    (
        "ai-signpost",
        re.compile(
            r"\b(let'?s (?:dive|explore|break this down)|here'?s what|"
            r"it is important to note|in conclusion|future looks bright|"
            r"serves as|stands as|underscores|showcases|unlocks?|unlocked|unlocking|"
            r"delve|delves|delved|delving)\b",
            re.I,
        ),
    ),
]


def iter_files(paths: list[Path]) -> list[Path]:
    out: list[Path] = []
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in TEXT_EXTS:
                out.append(path)
            continue
        for child in path.rglob("*"):
            if child.is_dir():
                continue
            if any(part in SKIP_PARTS for part in child.parts):
                continue
            if child.suffix.lower() in TEXT_EXTS:
                out.append(child)
    return sorted(set(out))


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return []
    hits: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        for label, pattern in PATTERNS:
            if pattern.search(stripped):
                hits.append((lineno, label, stripped[:220]))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()

    missing = [str(path) for path in args.paths if not path.exists()]
    if missing:
        parser.error(f"path does not exist: {', '.join(missing)}")

    count = 0
    for path in iter_files(args.paths):
        for lineno, label, line in scan_file(path):
            count += 1
            print(f"{path}:{lineno}: {label}: {line}")

    print(f"{count} candidate issue(s)")
    return 1 if count and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
