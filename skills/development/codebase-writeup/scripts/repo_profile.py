#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Build a read-only repository profile for a technical writeup."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

LANGUAGES = {
    ".c": "C", ".cc": "C++", ".cpp": "C++", ".cs": "C#", ".go": "Go",
    ".java": "Java", ".js": "JavaScript", ".jsx": "JavaScript", ".kt": "Kotlin",
    ".m": "Objective-C", ".mm": "Objective-C++", ".php": "PHP", ".py": "Python",
    ".rb": "Ruby", ".rs": "Rust", ".sh": "Shell", ".swift": "Swift",
    ".ts": "TypeScript", ".tsx": "TypeScript",
}
MANIFESTS = {
    "Cargo.toml", "CMakeLists.txt", "Gemfile", "Package.swift", "build.gradle", "go.mod",
    "package-lock.json", "package.json", "pnpm-lock.yaml", "pom.xml", "poetry.lock",
    "pyproject.toml", "requirements.txt", "yarn.lock",
}
ENTRYPOINTS = {
    "__main__.py", "app.py", "cli.py", "index.js", "index.mjs", "index.ts", "main.go",
    "main.py", "main.rs", "server.js", "server.py",
}
TEXT_SUFFIXES = set(LANGUAGES) | {".css", ".html", ".json", ".md", ".toml", ".txt", ".yaml", ".yml"}
DOC_SUFFIXES = {".md", ".mdx", ".rst"}
SKIP_DIRS = {
    ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".venv", "__pycache__",
    "build", "coverage", "dist", "node_modules", "target", "vendor",
}
URL = re.compile(r"https?://[^\s'\"<>()]+", re.IGNORECASE)


def walk_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root):
        dirs[:] = sorted(directory for directory in dirs if directory not in SKIP_DIRS)
        base = Path(current)
        files.extend(base / name for name in sorted(names) if (base / name).is_file())
    return files


def repository_files(root: Path, include_ignored: bool) -> list[Path]:
    if not include_ignored:
        try:
            result = subprocess.run(
                ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            result = None
        if result is not None and result.returncode == 0:
            names = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
            return [root / name for name in names if name and (root / name).is_file()]
    return walk_files(root)


def collect(root: Path, include_ignored: bool) -> dict[str, object]:
    files = repository_files(root, include_ignored)
    languages = Counter(LANGUAGES[path.suffix.lower()] for path in files if path.suffix.lower() in LANGUAGES)
    domains: Counter[str] = Counter()
    for path in files:
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            if path.stat().st_size > 2_000_000:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in URL.findall(text):
            hostname = urlsplit(match.rstrip(".,;]")).hostname
            if hostname:
                domains[hostname.lower()] += 1
    large_files = []
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > 262_144:
            large_files.append({"path": path.relative_to(root).as_posix(), "bytes": size})
    large_files.sort(key=lambda item: (-int(item["bytes"]), str(item["path"])))
    return {
        "root": str(root),
        "files": len(files),
        "languages": dict(languages.most_common()),
        "manifests": sorted(path.relative_to(root).as_posix() for path in files if path.name in MANIFESTS),
        "entrypoint_candidates": sorted(path.relative_to(root).as_posix() for path in files if path.name in ENTRYPOINTS),
        "documentation": sorted(path.relative_to(root).as_posix() for path in files if path.suffix.lower() in DOC_SUFFIXES),
        "external_domains": dict(domains.most_common()),
        "large_files": large_files[:20],
    }


def print_text(report: dict[str, object]) -> None:
    print(f"Repository: {report['root']}")
    print(f"Files: {report['files']}")
    for heading, key in (
        ("Languages", "languages"), ("Manifests", "manifests"),
        ("Entry-point candidates", "entrypoint_candidates"), ("Documentation", "documentation"),
        ("External domains", "external_domains"), ("Large files", "large_files"),
    ):
        print(f"\n{heading}:")
        values = report[key]
        if not values:
            print("  (none)")
        elif isinstance(values, dict):
            for name, count in values.items():
                print(f"  {name}: {count}")
        elif key == "large_files":
            for item in values:
                print(f"  {item['path']} ({item['bytes']} bytes)")
        else:
            for value in values:
                print(f"  {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", type=Path)
    parser.add_argument("--include-ignored", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {args.path}")
    report = collect(root, args.include_ignored)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
