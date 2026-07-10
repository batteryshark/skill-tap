#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate portable skill packages in this repository."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
REQUIRED_DIRS = ("agents", "bin", "references", "scripts")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^]]*]\(([^)]+)\)")


def scalar(value: str) -> str:
    value = value.strip()
    if value[:1] in {"'", '"'}:
        parsed = ast.literal_eval(value)
        if not isinstance(parsed, str):
            raise ValueError("frontmatter values must be strings")
        return parsed
    return value


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"unsupported frontmatter line: {line!r}")
        key, value = line.split(":", 1)
        key = key.strip()
        if key in metadata:
            raise ValueError(f"duplicate frontmatter key: {key}")
        metadata[key] = scalar(value)
    return metadata, "\n".join(lines[end + 1 :]).strip()


def validate_links(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    for target in LINK_RE.findall(text):
        target = target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        file_target = target.split("#", 1)[0]
        if file_target and not (path.parent / file_target).exists():
            errors.append(f"{path.relative_to(ROOT)}: broken link to {target}")
    return errors


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    relative = skill_dir.relative_to(ROOT)
    name = skill_dir.name
    if not NAME_RE.fullmatch(name):
        errors.append(f"{relative}: invalid directory name")

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"{relative}: missing SKILL.md"]
    try:
        metadata, body = parse_frontmatter(skill_md)
    except (SyntaxError, ValueError) as exc:
        return [f"{skill_md.relative_to(ROOT)}: {exc}"]

    if set(metadata) != {"name", "description"}:
        errors.append(
            f"{skill_md.relative_to(ROOT)}: frontmatter must contain only name and description"
        )
    if metadata.get("name") != name:
        errors.append(f"{skill_md.relative_to(ROOT)}: name must match {name}")
    if len(metadata.get("description", "").strip()) < 40:
        errors.append(f"{skill_md.relative_to(ROOT)}: description is too short to trigger reliably")
    if not body:
        errors.append(f"{skill_md.relative_to(ROOT)}: empty instructions")

    for dirname in REQUIRED_DIRS:
        directory = skill_dir / dirname
        if not directory.is_dir():
            errors.append(f"{relative}: missing {dirname}/")
        elif not any(path.is_file() for path in directory.iterdir()):
            errors.append(f"{relative}: {dirname}/ has no useful files")

    command = skill_dir / "bin" / name
    if command.exists() and not command.stat().st_mode & 0o111:
        errors.append(f"{command.relative_to(ROOT)}: entry point is not executable")
    elif not command.is_file():
        errors.append(f"{relative}: missing bin/{name}")

    for path in (skill_dir / "agents").glob("*") if (skill_dir / "agents").is_dir() else []:
        if path.suffix.lower() not in {".md", ".txt"}:
            errors.append(f"{path.relative_to(ROOT)}: agents/ accepts portable prompts only")

    for path in skill_dir.rglob("*.py"):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:8])
        if "# /// script" not in head or "# ///" not in head:
            errors.append(f"{path.relative_to(ROOT)}: missing PEP 723 metadata")

    for path in skill_dir.rglob("*.ts"):
        if not path.with_suffix(".mjs").is_file():
            errors.append(f"{path.relative_to(ROOT)}: missing compiled .mjs sibling")

    for path in skill_dir.rglob("*.md"):
        errors.extend(validate_links(path))
    return errors


def main() -> int:
    skill_files = sorted(SKILLS_ROOT.glob("*/*/SKILL.md"))
    if not skill_files:
        print("No skills found", file=sys.stderr)
        return 1

    errors: list[str] = []
    for skill_file in skill_files:
        errors.extend(validate_skill(skill_file.parent))
    for path in (ROOT / "README.md", ROOT / "SKILL-CONTRACT.md"):
        errors.extend(validate_links(path))

    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Validated {len(skill_files)} skill package(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
