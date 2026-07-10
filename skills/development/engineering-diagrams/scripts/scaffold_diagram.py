#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a portable Markdown scaffold for an engineering diagram."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


TEMPLATES = {
    "system": """flowchart LR
  actor[\"Actor\"] --> entry[\"Entry point\"]
  entry --> system[\"System\"]
  system --> store[(\"Data store\")]
  system --> external[\"External system\"]""",
    "component": """flowchart LR
  entry[\"Entry component\\nOwns: ...\"] -->|interface| core[\"Core component\\nOwns: ...\"]
  core --> data[\"Data component\\nOwns: ...\"]""",
    "data-flow": """flowchart LR
  source[\"Input source\"] --> validate[\"Validate\"]
  validate --> transform[\"Transform\"]
  transform --> store[(\"Store\")]
  transform --> output[\"Output or side effect\"]""",
    "sequence": """sequenceDiagram
  actor Actor
  participant Entry
  participant Core
  Actor->>Entry: Request
  Entry->>Core: Validate and execute
  Core-->>Entry: Result
  Entry-->>Actor: Response""",
    "state": """stateDiagram-v2
  [*] --> Initial
  Initial --> Active: trigger [guard]
  Active --> Complete: terminal event
  Complete --> [*]""",
    "trust-boundary": """flowchart LR
  untrusted[\"Untrusted input\"] --> gateway[\"Validation and identity checks\"]
  subgraph trusted[\"Trusted boundary\"]
    gateway --> service[\"Service\"]
    service --> store[(\"Sensitive store\")]
  end
  service --> external[\"External party\"]""",
}


def render(kind: str, title: str) -> str:
    return f"""# {title}

Question: What should this diagram help a reader understand?

Scope: Name the scenario, subsystem, and exclusions.

```mermaid
{TEMPLATES[kind]}
```

## Legend

- Solid relationships are observed in implementation or reproduced behavior.
- Dashed relationships are inferred or documented but not yet verified.

## Evidence and uncertainty

- Replace this item with paths, symbols, schemas, logs, or test scenarios.
- Record material omissions and questions here.
"""


def write_output(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=sorted(TEMPLATES))
    parser.add_argument("--title", help="diagram title")
    parser.add_argument("--output", type=Path, help="write to this Markdown file")
    parser.add_argument("--force", action="store_true", help="overwrite --output")
    args = parser.parse_args()

    title = args.title or args.kind.replace("-", " ").title()
    content = render(args.kind, title)
    if args.output is None:
        print(content, end="")
        return 0
    try:
        write_output(args.output.expanduser(), content, args.force)
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
