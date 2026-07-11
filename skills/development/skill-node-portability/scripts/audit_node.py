#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Inventory Node.js portability evidence in a skill package."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

IMPORT_RE = re.compile(r"(?:from\s+|import\s*\(|require\s*\()[\"']([^\"']+)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill")
    args = parser.parse_args()
    skill = Path(args.skill).expanduser().resolve()
    if not (skill / "SKILL.md").is_file():
        parser.error("target does not contain SKILL.md")
    files = []
    for path in sorted(item for item in skill.rglob("*") if item.suffix in {".js", ".mjs", ".cjs", ".ts"}):
        source = path.read_text(encoding="utf-8", errors="replace")
        specifiers = sorted(set(IMPORT_RE.findall(source)))
        third_party = [item for item in specifiers if not item.startswith((".", "/", "node:"))]
        files.append({"path": str(path.relative_to(skill)), "module_type": path.suffix, "third_party_specifiers": third_party, "compiled_mjs_sibling": path.suffix != ".ts" or path.with_suffix(".mjs").is_file()})
    package_files = [str(path.relative_to(skill)) for path in skill.rglob("package.json")]
    lock_files = [str(path.relative_to(skill)) for path in skill.rglob("package-lock.json")]
    print(json.dumps({"skill": str(skill), "scripts": files, "package_files": package_files, "lock_files": lock_files}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
