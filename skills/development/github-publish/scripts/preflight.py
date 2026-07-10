#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Run a read-only local preflight before publishing a project to GitHub."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "__pycache__", "build", "dist", "node_modules", "target"}
JUNK_NAMES = {".DS_Store", "Thumbs.db"}
SECRET_NAMES = {".env", "credentials.json", "secrets.json", "secrets.yaml", "secrets.yml"}


def git(root: Path, *args: str) -> tuple[int, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        return 127, ""
    return result.returncode, result.stdout.strip()


def visible_files(root: Path, in_git: bool) -> list[Path]:
    if in_git:
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
            return sorted(root / name for name in names if name and (root / name).is_file())
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not any(part in SKIP_DIRS for part in path.relative_to(root).parts)
    )


def collect(root: Path) -> dict[str, object]:
    repo_code, repo_text = git(root, "rev-parse", "--is-inside-work-tree")
    in_git = repo_code == 0 and repo_text == "true"
    files = visible_files(root, in_git)
    names_lower = {path.name.lower() for path in files}
    _, branch = git(root, "branch", "--show-current") if in_git else (1, "")
    _, status = git(root, "status", "--porcelain") if in_git else (1, "")
    _, remotes = git(root, "remote", "-v") if in_git else (1, "")
    name_code, author_name = git(root, "config", "user.name")
    email_code, author_email = git(root, "config", "user.email")

    secret_files = [
        path.relative_to(root).as_posix()
        for path in files
        if path.name.lower() in SECRET_NAMES or path.name.lower().startswith(".env.")
    ]
    junk_files = [
        path.relative_to(root).as_posix()
        for path in files
        if path.name in JUNK_NAMES or path.suffix.lower() in {".bak", ".log", ".orig", ".pyc", ".swp"}
    ]
    large_files = []
    for path in files:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > 1_000_000:
            large_files.append({"path": path.relative_to(root).as_posix(), "bytes": size})

    return {
        "root": str(root),
        "git_available": repo_code != 127,
        "git_repository": in_git,
        "branch": branch,
        "dirty_entries": len(status.splitlines()) if status else 0,
        "remotes": remotes.splitlines() if remotes else [],
        "author_name_configured": name_code == 0 and bool(author_name),
        "author_email_configured": email_code == 0 and bool(author_email),
        "readme": "readme.md" in names_lower,
        "license": any(name.startswith(("license", "copying")) for name in names_lower),
        "gitignore": ".gitignore" in names_lower,
        "secret_bearing_files": secret_files,
        "junk_files": junk_files,
        "large_files": sorted(large_files, key=lambda item: (-int(item["bytes"]), str(item["path"]))),
    }


def print_text(report: dict[str, object]) -> None:
    for key in (
        "root",
        "git_available",
        "git_repository",
        "branch",
        "dirty_entries",
        "author_name_configured",
        "author_email_configured",
        "readme",
        "license",
        "gitignore",
    ):
        print(f"{key}: {report[key]}")
    for key in ("remotes", "secret_bearing_files", "junk_files", "large_files"):
        print(f"{key}:")
        values = list(report[key])
        if not values:
            print("  (none)")
        for value in values:
            if isinstance(value, dict):
                print(f"  {value['path']} ({value['bytes']} bytes)")
            else:
                print(f"  {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {args.path}")
    report = collect(root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
