#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scaffold a portable Markdown agent role prompt."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--target-dir", default=".")
    args = parser.parse_args()
    if not NAME_RE.fullmatch(args.name):
        parser.error("name must use lowercase kebab-case")
    target = Path(args.target_dir).expanduser().resolve() / f"{args.name}.md"
    if target.exists():
        parser.error(f"target already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    title = args.name.replace("-", " ").title()
    target.write_text(f'''# {title}

## Purpose

{args.purpose.strip()}

## Inputs

- Describe required artifacts and task context.

## Evidence standard

- Separate observed facts from inference.
- Cite the artifact location for consequential findings.
- Report missing or inaccessible evidence.

## Constraints

- Stay within the assigned scope.
- Do not modify external state unless the task explicitly authorizes it.
- Do not assume the intended answer.

## Output

Return findings, supporting evidence, uncertainty, and the recommended next step.
''', encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
