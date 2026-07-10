#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scaffold and inspect compact project-tracker files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

TIMESTAMP = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}$")


def project_root(value: str) -> Path:
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {value}", file=sys.stderr)
        raise SystemExit(2)
    return root


def slug(value: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return cleaned or "session"


def tracker_text(title: str, date: str) -> str:
    return f"""# Project Tracker: {title}

Updated: {date}

## Current state

- Objective:
- Status:
- Main constraint:
- Blocked on:
- Next action:

## Active workstreams

- None recorded.

## Important paths and artifacts

- None recorded.

## Recent attempts and results

- None recorded.

## Decisions

- None recorded.

## Open questions and theories

- None recorded.

## Completed or resolved

- None recorded.
"""


def session_text(title: str, timestamp: str) -> str:
    date = dt.datetime.strptime(timestamp, "%Y-%m-%d-%H%M").strftime("%Y-%m-%d %H:%M")
    return f"""# Session: {title}

Date: {date}

## Starting context

## Work performed

## Evidence and results

## Decisions and pivots

## Artifacts

## Open questions

## Next actions
"""


def write_new(path: Path, content: str, dry_run: bool) -> bool:
    if path.exists():
        return False
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return True


def command_init(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    path = root / ".project" / "tracker.md"
    title = args.title or root.name
    created = write_new(path, tracker_text(title, dt.date.today().isoformat()), args.dry_run)
    print(json.dumps({"project": str(root), "path": str(path), "created": created, "dry_run": args.dry_run}, indent=2))
    return 0


def command_session(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    timestamp = args.timestamp or dt.datetime.now().astimezone().strftime("%Y-%m-%d-%H%M")
    if not TIMESTAMP.fullmatch(timestamp):
        print("ERROR: --timestamp must use YYYY-MM-DD-HHMM", file=sys.stderr)
        return 2
    try:
        dt.datetime.strptime(timestamp, "%Y-%m-%d-%H%M")
    except ValueError as exc:
        print(f"ERROR: invalid timestamp: {exc}", file=sys.stderr)
        return 2
    path = root / ".project" / "sessions" / f"{timestamp}-{slug(args.title)}.md"
    created = write_new(path, session_text(args.title, timestamp), args.dry_run)
    print(json.dumps({"project": str(root), "path": str(path), "created": created, "dry_run": args.dry_run}, indent=2))
    return 0


def command_status(args: argparse.Namespace) -> int:
    root = project_root(args.project)
    tracker = root / ".project" / "tracker.md"
    sessions_dir = root / ".project" / "sessions"
    sessions = sorted(sessions_dir.glob("*.md")) if sessions_dir.is_dir() else []
    payload = {
        "project": str(root),
        "tracker": str(tracker),
        "tracker_exists": tracker.is_file(),
        "sessions": len(sessions),
        "latest_session": str(sessions[-1]) if sessions else None,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for key, value in payload.items():
            print(f"{key}: {value}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init", help="create .project/tracker.md if missing")
    init.add_argument("project", nargs="?", default=".")
    init.add_argument("--title")
    init.add_argument("--dry-run", action="store_true")
    init.set_defaults(handler=command_init)

    session = subparsers.add_parser("session", help="create a timestamped session scaffold")
    session.add_argument("project", nargs="?", default=".")
    session.add_argument("--title", required=True)
    session.add_argument("--timestamp")
    session.add_argument("--dry-run", action="store_true")
    session.set_defaults(handler=command_session)

    status = subparsers.add_parser("status", help="inspect tracker state")
    status.add_argument("project", nargs="?", default=".")
    status.add_argument("--json", action="store_true")
    status.set_defaults(handler=command_status)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.handler(args))


if __name__ == "__main__":
    raise SystemExit(main())
