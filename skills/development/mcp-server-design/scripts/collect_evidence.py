#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory FastMCP architecture concerns in Python source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    groups = {"tools": ["@mcp.tool", ".tool("], "providers": ["Provider("], "transforms": ["Transform(", "CodeMode(", "ToolSearch("], "interaction": ["elicit(", "FastMCPApp", "app=True"], "security": ["auth=", "authorization=", "destructiveHint"], "lifecycle": ["lifespan", "TaskConfig", "timeout="]}
    found = {key: [] for key in groups}
    for path in workspace.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for key, needles in groups.items():
            if any(needle in text for needle in needles):
                found[key].append(str(path.relative_to(workspace)))
    print(json.dumps({"workspace": str(workspace), "concerns": found}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
