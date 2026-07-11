#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Locate FastMCP elicitation and Apps interaction surfaces."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    needles = ("elicit(", "FastMCPApp", "app=True", "Approval", "FormInput", "FileUpload", "Choice")
    hits = []
    for path in workspace.rglob("*.py"):
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if any(needle in line for needle in needles):
                hits.append({"file": str(path.relative_to(workspace)), "line": number, "text": line.strip()[:240]})
    print(json.dumps({"workspace": str(workspace), "interactions": hits}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
