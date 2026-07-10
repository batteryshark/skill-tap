#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Print a small, read-only map of a repository."""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".agent-work",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "vendor",
}
MANIFESTS = {
    "Cargo.toml",
    "Dockerfile",
    "Gemfile",
    "Makefile",
    "Package.swift",
    "build.gradle",
    "go.mod",
    "package.json",
    "pom.xml",
    "pyproject.toml",
    "requirements.txt",
}
ENTRYPOINT_NAMES = {
    "__main__.py",
    "app.py",
    "cli.py",
    "index.js",
    "index.mjs",
    "index.ts",
    "main.go",
    "main.py",
    "main.rs",
    "server.py",
}


def map_repository(root: Path) -> dict[str, object]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(directory for directory in dirs if directory not in SKIP_DIRS)
        base = Path(current)
        files.extend(base / name for name in sorted(names))

    relative = [path.relative_to(root) for path in files]
    top_level = Counter(path.parts[0] for path in relative if path.parts)
    extensions = Counter(path.suffix.lower() or "[no extension]" for path in relative)
    manifests = [str(path) for path in relative if path.name in MANIFESTS]
    entrypoints = [str(path) for path in relative if path.name in ENTRYPOINT_NAMES]
    docs = [str(path) for path in relative if path.suffix.lower() in {".md", ".mdx", ".rst"}]

    return {
        "root": str(root),
        "file_count": len(relative),
        "top_level": dict(top_level.most_common()),
        "manifests": manifests,
        "entrypoint_candidates": entrypoints,
        "documentation": docs,
        "extensions": dict(extensions.most_common(12)),
    }


def print_text(report: dict[str, object]) -> None:
    print(f"Repository: {report['root']}")
    print(f"Files: {report['file_count']}")
    for heading, key in (
        ("Top level", "top_level"),
        ("Manifests", "manifests"),
        ("Entry-point candidates", "entrypoint_candidates"),
        ("Documentation", "documentation"),
        ("File types", "extensions"),
    ):
        print(f"\n{heading}:")
        values = report[key]
        if not values:
            print("  (none found)")
        elif isinstance(values, dict):
            for name, count in values.items():
                print(f"  {name}: {count}")
        else:
            for value in values:
                print(f"  {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", type=Path)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {args.path}")

    report = map_repository(root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
