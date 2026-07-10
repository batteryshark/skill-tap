#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory an archived codebase and find exact duplicate files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

LANGUAGES = {
    ".asm": "Assembly", ".c": "C", ".cc": "C++", ".cpp": "C++", ".cs": "C#",
    ".go": "Go", ".h": "C/C++ header", ".hpp": "C++ header", ".java": "Java",
    ".js": "JavaScript", ".kt": "Kotlin", ".m": "Objective-C", ".mm": "Objective-C++",
    ".pas": "Pascal", ".py": "Python", ".rb": "Ruby", ".rs": "Rust",
    ".sh": "Shell", ".swift": "Swift", ".ts": "TypeScript",
}
MANIFESTS = {
    "Cargo.toml", "CMakeLists.txt", "Gemfile", "Makefile", "Package.swift", "build.gradle",
    "go.mod", "package.json", "pom.xml", "pyproject.toml", "requirements.txt", "setup.py",
}
GENERATED_DIRS = {
    ".git", ".venv", "__pycache__", "build", "coverage", "dist", "node_modules", "target", "vendor",
}
ARCHIVES = {".7z", ".bz2", ".gz", ".rar", ".tar", ".tgz", ".xz", ".zip"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def collect_files(root: Path, include_hidden: bool, include_generated: bool) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    broken_links: list[str] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        base = Path(current)
        dirs[:] = [
            directory for directory in sorted(dirs)
            if directory != ".git"
            and (include_generated or directory not in GENERATED_DIRS)
            and (include_hidden or not directory.startswith("."))
        ]
        for name in sorted(names):
            if not include_hidden and name.startswith("."):
                continue
            path = base / name
            if path.is_symlink() and not path.exists():
                broken_links.append(path.relative_to(root).as_posix())
            elif path.is_file():
                files.append(path)
    return files, broken_links


def duplicate_groups(files: list[Path], root: Path) -> list[dict[str, object]]:
    sizes: defaultdict[int, list[Path]] = defaultdict(list)
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size:
            sizes[size].append(path)
    groups: list[dict[str, object]] = []
    for size, candidates in sizes.items():
        if len(candidates) < 2:
            continue
        hashes: defaultdict[str, list[Path]] = defaultdict(list)
        for path in candidates:
            try:
                hashes[sha256(path)].append(path)
            except OSError:
                continue
        for digest, matches in hashes.items():
            if len(matches) > 1:
                groups.append({
                    "sha256": digest,
                    "bytes": size,
                    "paths": sorted(path.relative_to(root).as_posix() for path in matches),
                })
    groups.sort(key=lambda group: (-int(group["bytes"]), list(group["paths"])))
    return groups


def collect(root: Path, include_hidden: bool, include_generated: bool, hash_duplicates: bool) -> dict[str, object]:
    files, broken_links = collect_files(root, include_hidden, include_generated)
    languages = Counter(LANGUAGES[path.suffix.lower()] for path in files if path.suffix.lower() in LANGUAGES)
    extensions = Counter(path.suffix.lower() or "[no extension]" for path in files)
    return {
        "root": str(root),
        "files": len(files),
        "bytes": sum(path.stat().st_size for path in files if path.exists()),
        "languages": dict(languages.most_common()),
        "extensions": dict(extensions.most_common(15)),
        "manifests": sorted(path.relative_to(root).as_posix() for path in files if path.name in MANIFESTS),
        "archives": sorted(path.relative_to(root).as_posix() for path in files if path.suffix.lower() in ARCHIVES),
        "broken_links": sorted(broken_links),
        "duplicate_groups": duplicate_groups(files, root) if hash_duplicates else [],
    }


def print_text(report: dict[str, object]) -> None:
    print(f"Target: {report['root']}")
    print(f"Files: {report['files']}")
    print(f"Bytes: {report['bytes']}")
    for heading, key in (
        ("Languages", "languages"), ("Manifests", "manifests"), ("Archives", "archives"),
        ("Broken links", "broken_links"), ("Exact duplicate groups", "duplicate_groups"),
    ):
        print(f"\n{heading}:")
        values = report[key]
        if not values:
            print("  (none)")
        elif isinstance(values, dict):
            for name, count in values.items():
                print(f"  {name}: {count}")
        elif key == "duplicate_groups":
            for group in values:
                print(f"  {group['sha256']} ({group['bytes']} bytes)")
                for path in group["paths"]:
                    print(f"    {path}")
        else:
            for value in values:
                print(f"  {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", type=Path)
    parser.add_argument("--include-hidden", action="store_true")
    parser.add_argument("--include-generated", action="store_true")
    parser.add_argument("--no-hash", action="store_true", help="skip exact duplicate hashing")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {args.path}")
    report = collect(root, args.include_hidden, args.include_generated, not args.no_hash)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
