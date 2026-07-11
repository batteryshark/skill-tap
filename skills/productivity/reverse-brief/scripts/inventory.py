#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect a bounded repository inventory for a reverse brief."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    ignored = {".git", "node_modules", ".venv", "dist", "build"}
    files = []
    for path in workspace.rglob("*"):
        if path.is_file() and not any(part in ignored for part in path.parts):
            files.append(str(path.relative_to(workspace)))
    priority = [f for f in files if Path(f).name.lower() in {"readme.md", "pyproject.toml", "package.json", "cargo.toml", "go.mod", "makefile"} or "test" in f.lower()]
    print(json.dumps({"workspace": str(workspace), "priority_evidence": sorted(priority)[:150], "files": sorted(files)[:500], "truncated": len(files) > 500}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
