#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory publish-readiness risks without modifying the repository."""

from __future__ import annotations

import argparse
import re
import subprocess
from collections import Counter
from pathlib import Path

SKIP_DIRS = {
    ".agent-work",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
}
TEXT_SUFFIXES = {
    ".c",
    ".cpp",
    ".css",
    ".go",
    ".h",
    ".html",
    ".java",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".mjs",
    ".py",
    ".rb",
    ".rs",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
DOC_SUFFIXES = {".md", ".mdx", ".rst", ".txt"}
JUNK_PATH = re.compile(
    r"(^|/)(\.DS_Store|Thumbs\.db|.*\.(bak|orig|rej|swp|tmp|log|pyc)|"
    r"__pycache__/|node_modules/|\.venv/|dist/|build/|coverage/|\.pytest_cache/)",
    re.IGNORECASE,
)
SCRATCH_PATH = re.compile(
    r"(^|/|[-_.])(notes?|todo|scratch(?:pad)?|draft|wip|brainstorm|journal|"
    r"dev[-_]?notes|implementation[-_]?notes|review[-_]?output|old|backup|final)([-_./]|$)",
    re.IGNORECASE,
)
DEBT = re.compile(r"\b(TODO|FIXME|HACK|XXX|WIP|KLUDGE)\b")
LOCAL_PATH = re.compile(r"(?:/Users/[A-Za-z0-9._-]+|/home/[a-z][A-Za-z0-9._-]*|[A-Z]:\\\\Users\\\\)")
SLOP = re.compile(
    r"\b(delve|leverage|utiliz\w*|seamless\w*|robust|comprehensive|powerful|"
    r"unlock|elevate|plethora|myriad|cutting[- ]edge|game[- ]chang\w*|"
    r"blazingly)\b|it'?s worth noting|in today'?s|in the (world|realm) of|"
    r"when it comes to",
    re.IGNORECASE,
)
SECRET_VALUE = re.compile(
    r"(?:api[_-]?key|secret|token|password)\s*[=:]\s*['\"][^'\"]{6,}['\"]|"
    r"AKIA[0-9A-Z]{16}|-----BEGIN [A-Z ]*PRIVATE KEY",
    re.IGNORECASE,
)
SECRET_FILE = re.compile(
    r"(^|/)\.env($|\.)|(^|/)secrets?\.(json|ya?ml|txt|toml)$|"
    r"(^|/)credentials?(\.|$)",
    re.IGNORECASE,
)


def tracked_files(root: Path) -> tuple[list[Path], bool]:
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--cached",
                "--others",
                "--exclude-standard",
                "-z",
            ],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        result = None
    if result is not None and result.returncode == 0:
        names = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
        return [root / name for name in names if name], True
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    ]
    return sorted(files), False


def readable_lines(path: Path) -> list[str]:
    try:
        if path.stat().st_size > 2_000_000:
            return []
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []


def collect(root: Path) -> dict[str, list[str]]:
    files, in_git = tracked_files(root)
    relative = [(path, path.relative_to(root).as_posix()) for path in files]
    top_level = Counter(name.split("/", 1)[0] for _, name in relative)
    sections: dict[str, list[str]] = {
        "Repository shape": [
            f"version controlled: {'yes' if in_git else 'no'}",
            f"files inspected: {len(files)}",
            *(f"{name}: {count}" for name, count in top_level.most_common()),
        ],
        "Tracked or visible junk": [],
        "Scratch-like paths": [],
        "Debt markers": [],
        "Absolute local paths": [],
        "Possible secrets": [],
        "Generated-sounding prose": [],
        "Documentation spread": [],
        "Large files": [],
    }

    for path, name in relative:
        if JUNK_PATH.search(name):
            sections["Tracked or visible junk"].append(name)
        if SCRATCH_PATH.search(name):
            sections["Scratch-like paths"].append(name)
        if SECRET_FILE.search(name):
            sections["Possible secrets"].append(f"{name}: secret-bearing filename")
        try:
            if path.stat().st_size > 262_144:
                sections["Large files"].append(f"{path.stat().st_size:>10}  {name}")
        except OSError:
            pass
        if path.suffix.lower() in DOC_SUFFIXES:
            sections["Documentation spread"].append(name)
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        for line_number, line in enumerate(readable_lines(path), 1):
            stripped = line.strip()
            location = f"{name}:{line_number}"
            if DEBT.search(stripped):
                sections["Debt markers"].append(f"{location}: {stripped[:180]}")
            if LOCAL_PATH.search(stripped):
                sections["Absolute local paths"].append(f"{location}: {stripped[:180]}")
            if SECRET_VALUE.search(stripped):
                sections["Possible secrets"].append(f"{location}: suspected secret value (redacted)")
            if path.suffix.lower() in DOC_SUFFIXES and SLOP.search(stripped):
                sections["Generated-sounding prose"].append(f"{location}: {stripped[:180]}")
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", type=Path)
    parser.add_argument("--limit", type=int, default=50, help="maximum lines per section")
    args = parser.parse_args()
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {args.path}")
    if args.limit < 1:
        parser.error("--limit must be positive")

    for heading, findings in collect(root).items():
        print(f"\n=== {heading} ===")
        if not findings:
            print("  (none found)")
            continue
        for finding in findings[: args.limit]:
            print(f"  {finding}")
        if len(findings) > args.limit:
            print(f"  ... {len(findings) - args.limit} more")
    print("\nReview these leads in context; nothing was modified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
