#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Audit a skill against the portable Skills Tap package contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED = ("agents", "bin", "references", "scripts")


def audit(skill: Path) -> dict:
    findings: list[dict[str, str]] = []
    name = skill.name
    if not NAME_RE.fullmatch(name):
        findings.append({"severity": "error", "message": "directory name is not lowercase kebab-case"})
    skill_md = skill / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    if not text.startswith("---\n"):
        findings.append({"severity": "error", "message": "SKILL.md frontmatter is missing"})
    else:
        parts = text.split("---", 2)
        metadata = [line.split(":", 1)[0].strip() for line in parts[1].splitlines() if ":" in line]
        if set(metadata) != {"name", "description"}:
            findings.append({"severity": "error", "message": "frontmatter must contain only name and description"})
        if f"name: {name}" not in parts[1]:
            findings.append({"severity": "error", "message": "frontmatter name does not match directory"})
    for directory in REQUIRED:
        path = skill / directory
        if not path.is_dir() or not any(item.is_file() for item in path.iterdir()):
            findings.append({"severity": "error", "message": f"{directory}/ is missing or empty"})
    command = skill / "bin" / name
    if not command.is_file():
        findings.append({"severity": "error", "message": f"bin/{name} is missing"})
    elif not command.stat().st_mode & 0o111:
        findings.append({"severity": "error", "message": f"bin/{name} is not executable"})
    for script in skill.rglob("*.py"):
        head = "\n".join(script.read_text(encoding="utf-8").splitlines()[:8])
        if "# /// script" not in head or "# ///" not in head:
            findings.append({"severity": "error", "message": f"{script.relative_to(skill)} lacks PEP 723 metadata"})
    forbidden = [item.name for item in skill.iterdir() if item.name in {"README.md", "CHANGELOG.md"}]
    for item in forbidden:
        findings.append({"severity": "warning", "message": f"remove auxiliary {item}"})
    return {"skill": str(skill), "errors": sum(item["severity"] == "error" for item in findings), "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill")
    args = parser.parse_args()
    path = Path(args.skill).expanduser().resolve()
    if not path.is_dir():
        parser.error(f"not a directory: {path}")
    report = audit(path)
    print(json.dumps(report, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
