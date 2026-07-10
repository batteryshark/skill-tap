#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Create a concise Markdown decision-record scaffold."""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path


STATUSES = ("proposed", "accepted", "rejected", "superseded", "deprecated")


def iso_date(value: str) -> str:
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc


def render(title: str, status: str, date: str) -> str:
    return f"""# Decision: {title}

- Status: {status}
- Date: {date}
- Owners:
- Supersedes:
- Superseded by:

## Context

State the problem, scope, evidence available now, and why a durable decision is needed.

## Constraints

- Record the conditions that materially shape the choice.

## Decision

State the chosen direction precisely enough to guide action.

## Alternatives considered

### Alternative

- Strengths:
- Why not selected under these constraints:

## Consequences

### Benefits

- Expected and observable benefit.

### Costs and risks

- Accepted cost, risk, migration, or follow-up obligation.

## Evidence, validation, and uncertainty

- Observed facts:
- Documented intent:
- Inferences:
- Unknowns requiring confirmation:
- Validation:

## Reconsider when

- Name a concrete condition that should reopen this decision.

## Related material

- Link requirements, implementation, measurements, incidents, or related records.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--status", choices=STATUSES, default="proposed")
    parser.add_argument("--date", type=iso_date, default=dt.date.today().isoformat())
    parser.add_argument("--output", type=Path, help="write to this Markdown file")
    parser.add_argument("--force", action="store_true", help="overwrite --output")
    args = parser.parse_args()

    content = render(args.title.strip(), args.status, args.date)
    if args.output is None:
        print(content, end="")
        return 0

    path = args.output.expanduser()
    if path.exists() and not args.force:
        print(f"ERROR: refusing to overwrite existing file: {path}", file=sys.stderr)
        return 2
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
