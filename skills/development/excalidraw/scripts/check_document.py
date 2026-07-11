#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate core Excalidraw document invariants and report layout warnings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file")
    args = parser.parse_args()
    path = Path(args.file).expanduser().resolve()
    document = json.loads(path.read_text(encoding="utf-8"))
    errors, warnings = [], []
    if document.get("type") != "excalidraw": errors.append("type must be excalidraw")
    elements = document.get("elements")
    if not isinstance(elements, list): errors.append("elements must be a list"); elements = []
    ids = [item.get("id") for item in elements if isinstance(item, dict)]
    if None in ids: errors.append("every element needs an id")
    if len(ids) != len(set(ids)): errors.append("element ids must be unique")
    for item in elements:
        if not isinstance(item, dict): continue
        if item.get("width", 0) < 0 or item.get("height", 0) < 0: errors.append(f"{item.get('id')}: negative dimensions")
        if item.get("type") == "text" and len(item.get("text", "")) > 120: warnings.append(f"{item.get('id')}: long label")
    print(json.dumps({"file": str(path), "elements": len(elements), "errors": errors, "warnings": warnings}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
