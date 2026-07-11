#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory version-sensitive MCP and FastMCP patterns in a project."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    needles = ("fastmcp", "mcp.server.fastmcp", "FastMCP", "Context", "mount(", "lifespan", "transport=", ".mcp.json")
    hits = []
    for path in workspace.rglob("*"):
        if not path.is_file() or path.suffix not in {".py", ".toml", ".json"}:
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, 1):
            if any(needle in line for needle in needles):
                hits.append({"file": str(path.relative_to(workspace)), "line": number, "text": line.strip()[:240]})
    print(json.dumps({"workspace": str(workspace), "findings": hits}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
