#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory source-code shape without assigning quality verdicts."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

LANGUAGES = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".go": "Go",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".mjs": "JavaScript",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".sh": "Shell",
    ".swift": "Swift",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
}
SKIP_DIRS = {
    ".agent-work",
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
DEBT = re.compile(r"\b(TODO|FIXME|HACK|XXX|KLUDGE)\b")


def is_test(path: Path) -> bool:
    lowered = [part.lower() for part in path.parts]
    name = path.name.lower()
    return "test" in lowered or "tests" in lowered or name.startswith("test_") or any(
        marker in name for marker in (".test.", ".spec.", "_test.")
    )


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


def collect(root: Path, top: int, include_ignored: bool) -> dict[str, object]:
    records: list[dict[str, object]] = []
    languages: Counter[str] = Counter()
    debt_total = 0
    for path in repository_files(root, include_ignored):
        language = LANGUAGES.get(path.suffix.lower())
        if not language:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        debt_count = sum(len(DEBT.findall(line)) for line in lines)
        debt_total += debt_count
        languages[language] += 1
        records.append(
            {
                "path": path.relative_to(root).as_posix(),
                "language": language,
                "lines": len(lines),
                "nonblank_lines": sum(bool(line.strip()) for line in lines),
                "max_line_length": max((len(line) for line in lines), default=0),
                "debt_markers": debt_count,
                "test": is_test(path.relative_to(root)),
            }
        )
    records.sort(key=lambda record: (-int(record["lines"]), str(record["path"])))
    return {
        "root": str(root),
        "source_files": len(records),
        "test_files": sum(bool(record["test"]) for record in records),
        "languages": dict(languages.most_common()),
        "debt_markers": debt_total,
        "largest_files": records[:top],
    }


def print_text(report: dict[str, object]) -> None:
    print(f"Repository: {report['root']}")
    print(f"Source files: {report['source_files']}")
    print(f"Test files: {report['test_files']}")
    print(f"Debt markers: {report['debt_markers']}")
    print("Languages:")
    for language, count in dict(report["languages"]).items():
        print(f"  {language}: {count}")
    print("Largest source files:")
    for record in list(report["largest_files"]):
        test_label = " [test]" if record["test"] else ""
        print(
            f"  {record['lines']:>6} lines  {record['path']}"
            f" ({record['language']}){test_label}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", type=Path)
    parser.add_argument("--top", type=int, default=20, help="number of largest files to show")
    parser.add_argument("--include-ignored", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.path.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"not a directory: {args.path}")
    if args.top < 1:
        parser.error("--top must be positive")
    report = collect(root, args.top, args.include_ignored)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
