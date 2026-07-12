#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scaffold a standalone skill that conforms to the Skill Tap contract."""

from __future__ import annotations

import argparse
import json
import re
import stat
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def write(path: Path, content: str, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    if executable:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def scaffold(name: str, description: str, target_dir: Path) -> Path:
    if not NAME_RE.fullmatch(name):
        raise ValueError("name must use lowercase kebab-case")
    if len(description.strip()) < 40:
        raise ValueError("description must be at least 40 characters")
    skill = target_dir.expanduser().resolve() / name
    if skill.exists():
        raise FileExistsError(f"target already exists: {skill}")
    skill.mkdir(parents=True)

    write(skill / "SKILL.md", f'''---
name: {name}
description: {json.dumps(description.strip())}
---

# {name.replace('-', ' ').title()}

1. Inspect the request and required evidence.
2. Run `bin/{name}` against the target workspace.
3. Apply the workflow-specific judgment described in this skill.
4. Verify the result and report limitations.

Read [references/evidence-guide.md](references/evidence-guide.md) when interpreting collected evidence. Use [agents/reviewer.md](agents/reviewer.md) for an independent evidence pass when the decision is consequential.
''')
    write(skill / "agents" / "reviewer.md", f'''# {name.replace('-', ' ').title()} reviewer

Review the supplied evidence for this skill's task. Separate facts from inference, identify missing evidence, apply the documented constraints, and return findings plus a verification recommendation.
''')
    write(skill / "references" / "evidence-guide.md", '''# Evidence guide

Replace this file with domain-specific interpretation rules, known limitations, and examples. Keep detailed material here rather than expanding `SKILL.md`.
''')
    write(skill / "bin" / name, f'''#!/bin/sh
set -eu
skill_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if command -v uv >/dev/null 2>&1; then
  exec uv run --script "$skill_dir/scripts/collect_evidence.py" "$@"
fi
exec python3 "$skill_dir/scripts/collect_evidence.py" "$@"
''', executable=True)
    write(skill / "scripts" / "collect_evidence.py", f'''#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Collect minimal workspace evidence for {name}."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", nargs="?", default=".")
    args = parser.parse_args()
    workspace = Path(args.workspace).expanduser().resolve()
    files = sorted(str(path.relative_to(workspace)) for path in workspace.rglob("*") if path.is_file())
    print(json.dumps({{"skill": "{name}", "workspace": str(workspace), "files": files[:200], "truncated": len(files) > 200}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
''', executable=True)
    return skill


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name")
    parser.add_argument("--description", required=True)
    parser.add_argument("--target-dir", default=".")
    args = parser.parse_args()
    try:
        path = scaffold(args.name, args.description, Path(args.target_dir))
    except (ValueError, FileExistsError) as error:
        parser.error(str(error))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
