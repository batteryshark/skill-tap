#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Find repository-hygiene candidates for human review."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
TEXT_SUFFIXES = {
    ".c",
    ".cpp",
    ".go",
    ".h",
    ".java",
    ".js",
    ".json",
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
SCRATCH_NAME = re.compile(
    r"(^|[-_.])(notes?|todo|scratch(?:pad)?|draft|wip|brainstorm|handoff|"
    r"implementation[-_]?report|review[-_]?output|old|backup|final)([-_.]|$)",
    re.IGNORECASE,
)
DEBT_MARKER = re.compile(r"\b(TODO|FIXME|HACK|XXX|WIP|KLUDGE)\b")
LOCAL_PATH = re.compile(r"(?:/Users/[A-Za-z0-9._-]+|/home/[a-z][A-Za-z0-9._-]*|[A-Z]:\\\\Users\\\\)")
PROCESS_RESIDUE = re.compile(
    r"\b(session summary|agent report|prompt dump|chain of thought|review pass \d+)\b",
    re.IGNORECASE,
)


def iter_files(paths: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        if path.is_file():
            files.add(path)
            continue
        for child in path.rglob("*"):
            if child.is_dir() or any(part in SKIP_DIRS for part in child.parts):
                continue
            files.add(child)
    return sorted(files)


def scan(paths: list[Path]) -> list[tuple[Path, int, str, str]]:
    findings: list[tuple[Path, int, str, str]] = []
    for path in iter_files(paths):
        if SCRATCH_NAME.search(path.name):
            findings.append((path, 0, "scratch-name", path.name))
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(lines, 1):
            stripped = line.strip()
            for label, pattern in (
                ("debt-marker", DEBT_MARKER),
                ("absolute-local-path", LOCAL_PATH),
                ("process-residue", PROCESS_RESIDUE),
            ):
                if pattern.search(stripped):
                    findings.append((path, line_number, label, stripped[:220]))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()
    missing = [str(path) for path in args.paths if not path.exists()]
    if missing:
        parser.error(f"path does not exist: {', '.join(missing)}")

    findings = scan([path.resolve() for path in args.paths])
    for path, line_number, label, evidence in findings:
        location = f"{path}:{line_number}" if line_number else str(path)
        print(f"{location}: {label}: {evidence}")
    print(f"{len(findings)} candidate issue(s)")
    return 1 if findings and args.fail_on_findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
