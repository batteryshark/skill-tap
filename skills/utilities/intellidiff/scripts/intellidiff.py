#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Read-only file comparison, directory diff, hashing, and duplicate detection."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

SKIP_DIRS = {
    ".git",
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


def fail(message: str) -> "NoReturn":
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(2)


def require_file(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_file():
        fail(f"not a file: {value}")
    return path


def require_dir(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.is_dir():
        fail(f"not a directory: {value}")
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_binary(path: Path) -> bool:
    with path.open("rb") as handle:
        return b"\0" in handle.read(8192)


def normalize_text(data: bytes, args: argparse.Namespace) -> str:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"smart comparison requires UTF-8 text: {exc}")
    if args.ignore_newlines:
        text = text.replace("\r\n", "\n").replace("\r", "\n")
    if args.normalize_unicode:
        text = unicodedata.normalize("NFKC", text)
    if args.ignore_case:
        text = text.casefold()
    lines = text.splitlines(keepends=True)
    if args.ignore_whitespace:
        normalized = []
        for line in lines:
            ending = "\n" if line.endswith(("\n", "\r")) else ""
            normalized.append(line.rstrip("\r\n").strip() + ending)
        lines = normalized
    if args.ignore_blank:
        lines = [line for line in lines if line.strip()]
    return "".join(lines)


def emit(payload: dict[str, object], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2))
        return
    for key, value in payload.items():
        if isinstance(value, list):
            print(f"{key}:")
            if not value:
                print("  (none)")
            for item in value:
                print(f"  {item}")
        else:
            print(f"{key}: {value}")


def iter_files(root: Path, include_hidden: bool) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for current, dirs, names in os.walk(root, followlinks=False):
        kept = []
        for directory in sorted(dirs):
            if directory in SKIP_DIRS:
                continue
            if not include_hidden and directory.startswith("."):
                continue
            kept.append(directory)
        dirs[:] = kept
        base = Path(current)
        for name in sorted(names):
            if not include_hidden and name.startswith("."):
                continue
            path = base / name
            if path.is_file() and not path.is_symlink():
                files[path.relative_to(root).as_posix()] = path
    return files


def command_hash(args: argparse.Namespace) -> int:
    path = require_file(args.file)
    payload = {
        "path": str(path),
        "sha256": sha256(path),
        "bytes": path.stat().st_size,
        "binary": is_binary(path),
    }
    emit(payload, args.json)
    return 0


def command_file(args: argparse.Namespace) -> int:
    left = require_file(args.left)
    right = require_file(args.right)
    left_digest = sha256(left)
    right_digest = sha256(right)
    if args.smart:
        left_text = normalize_text(left.read_bytes(), args)
        right_text = normalize_text(right.read_bytes(), args)
        identical = left_text == right_text
        payload: dict[str, object] = {
            "result": "identical-normalized" if identical else "different",
            "mode": "smart",
            "left": str(left),
            "right": str(right),
            "left_sha256": left_digest,
            "right_sha256": right_digest,
            "normalizations": [
                name
                for enabled, name in (
                    (args.ignore_newlines, "newlines"),
                    (args.ignore_whitespace, "whitespace"),
                    (args.ignore_blank, "blank-lines"),
                    (args.ignore_case, "case"),
                    (args.normalize_unicode, "unicode-nfkc"),
                )
                if enabled
            ],
        }
        if not identical and not args.json:
            payload["diff"] = "\n".join(
                difflib.unified_diff(
                    left_text.splitlines(),
                    right_text.splitlines(),
                    fromfile=str(left),
                    tofile=str(right),
                    lineterm="",
                )
            )
    else:
        identical = left_digest == right_digest and left.read_bytes() == right.read_bytes()
        payload = {
            "result": "identical" if identical else "different",
            "mode": "exact",
            "left": str(left),
            "right": str(right),
            "left_sha256": left_digest,
            "right_sha256": right_digest,
        }
    emit(payload, args.json)
    return 0 if identical else 1


def command_folders(args: argparse.Namespace) -> int:
    left = require_dir(args.left)
    right = require_dir(args.right)
    left_files = iter_files(left, args.include_hidden)
    right_files = iter_files(right, args.include_hidden)
    common = sorted(set(left_files) & set(right_files))
    identical: list[str] = []
    changed: list[str] = []
    for relative in common:
        if sha256(left_files[relative]) == sha256(right_files[relative]):
            identical.append(relative)
        else:
            changed.append(relative)
    payload = {
        "result": "identical" if not changed and set(left_files) == set(right_files) else "different",
        "left": str(left),
        "right": str(right),
        "identical": identical,
        "changed": changed,
        "left_only": sorted(set(left_files) - set(right_files)),
        "right_only": sorted(set(right_files) - set(left_files)),
    }
    emit(payload, args.json)
    return 0 if payload["result"] == "identical" else 1


def command_duplicates(args: argparse.Namespace) -> int:
    root = require_dir(args.folder)
    files = iter_files(root, args.include_hidden)
    sizes: defaultdict[int, list[tuple[str, Path]]] = defaultdict(list)
    for relative, path in files.items():
        size = path.stat().st_size
        if size:
            sizes[size].append((relative, path))
    groups = []
    for size, matches in sizes.items():
        if len(matches) < 2:
            continue
        digests: defaultdict[str, list[str]] = defaultdict(list)
        for relative, path in matches:
            digests[sha256(path)].append(relative)
        for digest, paths in digests.items():
            if len(paths) > 1:
                groups.append({"sha256": digest, "bytes": size, "paths": sorted(paths)})
    groups.sort(key=lambda group: (-int(group["bytes"]), list(group["paths"])))
    payload = {"folder": str(root), "files": len(files), "duplicate_groups": groups}
    if args.json:
        emit(payload, True)
    else:
        print(f"folder: {root}")
        print(f"files: {len(files)}")
        print("duplicate_groups:")
        if not groups:
            print("  (none)")
        for group in groups:
            print(f"  {group['sha256']} ({group['bytes']} bytes)")
            for path in group["paths"]:
                print(f"    {path}")
    return 0


def command_lines(args: argparse.Namespace) -> int:
    path = require_file(args.file)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        fail(f"lines requires UTF-8 text: {exc}")
    if args.start < 1 or args.context < 0:
        fail("--start must be at least 1 and --context cannot be negative")
    end = len(lines) if args.end is None else args.end
    if end < args.start:
        fail("--end must be greater than or equal to --start")
    actual_start = max(1, args.start - args.context)
    actual_end = min(len(lines), end + args.context)
    for index in range(actual_start, actual_end + 1):
        marker = ">>>" if args.start <= index <= end else "   "
        print(f"{marker} {index:>6} | {lines[index - 1]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    hash_parser = subparsers.add_parser("hash", help="calculate SHA-256 and file metadata")
    hash_parser.add_argument("file")
    hash_parser.add_argument("--json", action="store_true")
    hash_parser.set_defaults(handler=command_hash)

    file_parser = subparsers.add_parser("file", help="compare two files")
    file_parser.add_argument("left")
    file_parser.add_argument("right")
    file_parser.add_argument("--smart", action="store_true", help="compare normalized UTF-8 text")
    file_parser.add_argument("--ignore-newlines", action="store_true")
    file_parser.add_argument("--ignore-whitespace", action="store_true")
    file_parser.add_argument("--ignore-blank", action="store_true")
    file_parser.add_argument("--ignore-case", action="store_true")
    file_parser.add_argument("--normalize-unicode", action="store_true")
    file_parser.add_argument("--json", action="store_true")
    file_parser.set_defaults(handler=command_file)

    folders_parser = subparsers.add_parser("folders", help="compare two directory trees")
    folders_parser.add_argument("left")
    folders_parser.add_argument("right")
    folders_parser.add_argument("--include-hidden", action="store_true")
    folders_parser.add_argument("--json", action="store_true")
    folders_parser.set_defaults(handler=command_folders)

    duplicates_parser = subparsers.add_parser("duplicates", help="find exact duplicate files")
    duplicates_parser.add_argument("folder")
    duplicates_parser.add_argument("--include-hidden", action="store_true")
    duplicates_parser.add_argument("--json", action="store_true")
    duplicates_parser.set_defaults(handler=command_duplicates)

    lines_parser = subparsers.add_parser("lines", help="read a one-based line range")
    lines_parser.add_argument("file")
    lines_parser.add_argument("--start", type=int, default=1)
    lines_parser.add_argument("--end", type=int)
    lines_parser.add_argument("--context", type=int, default=0)
    lines_parser.set_defaults(handler=command_lines)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
