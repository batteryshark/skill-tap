#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory or emit user-specified text sources for a project retrospective."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

TEXT_SUFFIXES = {".jsonl", ".log", ".md", ".mdx", ".rst", ".text", ".txt"}
SKIP_DIRS = {".git", ".venv", "__pycache__", "build", "dist", "node_modules", "target"}


def collect(paths: list[Path], include_hidden: bool) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        if path.is_file():
            if path.suffix.lower() in TEXT_SUFFIXES:
                files.add(path)
            continue
        for current, dirs, names in os.walk(path):
            dirs[:] = [
                directory for directory in sorted(dirs)
                if directory not in SKIP_DIRS and (include_hidden or not directory.startswith("."))
            ]
            base = Path(current)
            for name in sorted(names):
                if not include_hidden and name.startswith("."):
                    continue
                candidate = base / name
                if candidate.suffix.lower() in TEXT_SUFFIXES and candidate.is_file():
                    files.add(candidate)
    return sorted(files)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="+", type=Path)
    parser.add_argument("--include-hidden", action="store_true")
    parser.add_argument("--max-bytes", type=int, default=1_000_000)
    parser.add_argument("--emit", action="store_true", help="emit source contents after the manifest")
    parser.add_argument("--json", action="store_true", help="emit a JSON manifest; cannot combine with --emit")
    args = parser.parse_args()
    if args.emit and args.json:
        parser.error("--emit and --json cannot be combined")
    if args.max_bytes < 1:
        parser.error("--max-bytes must be positive")
    missing = [str(path) for path in args.sources if not path.expanduser().exists()]
    if missing:
        parser.error(f"source does not exist: {', '.join(missing)}")
    sources = [path.expanduser().resolve() for path in args.sources]
    files = collect(sources, args.include_hidden)
    manifest = []
    total = 0
    selected: list[Path] = []
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        included = total + size <= args.max_bytes
        manifest.append({"path": str(path), "bytes": size, "included": included})
        if included:
            selected.append(path)
            total += size
    payload = {"files_found": len(files), "files_included": len(selected), "bytes_included": total, "files": manifest}
    if args.json:
        print(json.dumps(payload, indent=2))
        return 0
    print(f"files_found: {len(files)}")
    print(f"files_included: {len(selected)}")
    print(f"bytes_included: {total}")
    for item in manifest:
        state = "included" if item["included"] else "skipped-limit"
        print(f"  [{state}] {item['path']} ({item['bytes']} bytes)")
    if args.emit:
        for path in selected:
            print(f"\n===== {path} =====")
            try:
                print(path.read_text(encoding="utf-8", errors="replace"), end="")
            except OSError as exc:
                print(f"\nERROR reading {path}: {exc}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
