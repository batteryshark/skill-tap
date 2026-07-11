#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory Python portability evidence in a skill package."""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill")
    args = parser.parse_args()
    skill = Path(args.skill).expanduser().resolve()
    if not (skill / "SKILL.md").is_file():
        parser.error("target does not contain SKILL.md")
    local = {path.stem for path in skill.rglob("*.py")}
    reports = []
    for path in sorted(skill.rglob("*.py")):
        source = path.read_text(encoding="utf-8")
        imports = set()
        try:
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.add(node.module.split(".")[0])
        except SyntaxError as error:
            reports.append({"path": str(path.relative_to(skill)), "syntax_error": str(error)})
            continue
        third_party = sorted(name for name in imports if name not in sys.stdlib_module_names and name not in local)
        head = "\n".join(source.splitlines()[:8])
        reports.append({"path": str(path.relative_to(skill)), "pep723": "# /// script" in head and "# ///" in head, "third_party_imports": third_party})
    command = skill / "bin" / skill.name
    print(json.dumps({"skill": str(skill), "scripts": reports, "matching_launcher": command.is_file(), "launcher_executable": command.is_file() and bool(command.stat().st_mode & 0o111)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
