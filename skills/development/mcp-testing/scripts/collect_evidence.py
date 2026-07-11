#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory FastMCP code and test coverage surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    source = []
    tests = []
    markers = {"client": 0, "elicitation": 0, "authorization": 0, "tasks": 0, "transport": 0}
    for path in workspace.rglob("*.py"):
        rel = str(path.relative_to(workspace))
        text = path.read_text(encoding="utf-8", errors="replace")
        if "FastMCP" in text or "@mcp." in text:
            source.append(rel)
        if path.name.startswith("test_") or "tests" in path.parts:
            tests.append(rel)
            for key, needle in {"client": "Client(", "elicitation": "elicit", "authorization": "authoriz", "tasks": "task", "transport": "http"}.items():
                markers[key] += text.lower().count(needle.lower())
    print(json.dumps({"workspace": str(workspace), "mcp_source": source, "tests": tests, "test_markers": markers}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
