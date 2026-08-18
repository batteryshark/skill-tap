#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Scan a goal/epic markdown document and report mechanical evidence.

Reports facts against references/STANDARD.md — section presence and order,
checkbox counts and grammar, boundary and budget markers, open questions.
It renders no verdict: judgment stays with the grader.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

SECTION_ORDER = [
    "Description",
    "Goal",
    "Requirements",
    "Acceptance Criteria",
    "Plan",
    "Notes",
]
CAPS = {"Requirements": 6, "Acceptance Criteria": 5}
CHECKBOX = re.compile(r"^- \[( |x|~)\] (.+)$")
DECLINE_SEPARATOR = " — "


def sections_of(text: str) -> dict[str, str]:
    found: dict[str, str] = {}
    current = None
    for line in text.splitlines():
        heading = re.fullmatch(r"##\s+(.+?)\s*", line)
        if heading:
            current = heading.group(1)
            found.setdefault(current, "")
            continue
        if current is not None:
            found[current] += line + "\n"
    return found


def scan(text: str) -> list[str]:
    lines: list[str] = []
    found = sections_of(text)

    present = [name for name in SECTION_ORDER if name in found]
    missing = [name for name in SECTION_ORDER if name not in found]
    order = [name for name in found if name in SECTION_ORDER]
    lines.append(f"sections present: {', '.join(present) or 'none'}")
    if missing:
        lines.append(f"sections missing: {', '.join(missing)}")
    if order != present:
        lines.append(f"section order differs from standard: {', '.join(order)}")

    goal = found.get("Goal", "").strip()
    if goal:
        sentences = [s for s in re.split(r"(?<=[.!?])\s+", goal) if s.strip()]
        lines.append(f"goal: {len(sentences)} sentence(s); 'so that' clause: "
                     f"{'yes' if re.search(r'\bso( that)?\b', goal) else 'no'}")

    for name, cap in CAPS.items():
        body = found.get(name, "")
        items = [m for m in map(CHECKBOX.fullmatch, body.splitlines()) if m]
        stray = [l for l in body.splitlines() if l.startswith("- [") and not CHECKBOX.fullmatch(l)]
        lines.append(f"{name.lower()}: {len(items)} item(s) (cap {cap})")
        for match in items:
            state, item_text = match.group(1), match.group(2)
            if state == "~" and DECLINE_SEPARATOR not in item_text:
                lines.append(f"  declined without reason: {item_text}")
            if item_text.rstrip().endswith("."):
                lines.append(f"  trailing period: {item_text}")
        for line in stray:
            lines.append(f"  malformed checkbox line: {line}")

    description = found.get("Description", "")
    lines.append("out of scope in Description: "
                 f"{'yes' if re.search(r'out of scope', description, re.I) else 'no'}")

    notes = found.get("Notes", "")
    lines.append(f"appetite line in Notes: {'yes' if re.search(r'^.{0,3}appetite:', notes, re.I | re.M) else 'no'}")
    open_questions = re.findall(r"^\s*-\s*Q:\s*(.+)$", notes, re.M)
    lines.append(f"unanswered Q: lines in Notes: {len(open_questions)}")
    for question in open_questions:
        lines.append(f"  Q: {question}")

    return lines


SAMPLE = """\
## Description
Things drift. Out of scope: the importer.

## Goal
Captures land offline so the phone works alone.

## Requirements
- [ ] Runs on the box
- [~] Old sync kept
- [x] One writer only.

## Acceptance Criteria
- [ ] With the laptop off, a capture lands

## Plan
Do it like the notes handler.

## Notes
Appetite: two evenings.
- Q: Which port?
"""


def self_test() -> int:
    report = "\n".join(scan(SAMPLE))
    assert "sections missing" not in report, report
    assert "requirements: 3 item(s) (cap 6)" in report, report
    assert "declined without reason: Old sync kept" in report, report
    assert "trailing period: One writer only." in report, report
    assert "out of scope in Description: yes" in report, report
    assert "appetite line in Notes: yes" in report, report
    assert "unanswered Q: lines in Notes: 1" in report, report
    assert "'so that' clause: yes" in report, report
    print("self-test passed")
    return 0


USAGE = """\
usage: goal-epic-craft FILE.md   scan a goal/epic document, print evidence
       goal-epic-craft --self-test
Reports facts against references/STANDARD.md; renders no verdict."""


def main(argv: list[str]) -> int:
    if argv and argv[0] in {"--help", "-h"}:
        print(USAGE)
        return 0
    if len(argv) != 1:
        print(USAGE, file=sys.stderr)
        return 2
    if argv[0] == "--self-test":
        return self_test()
    path = Path(argv[0])
    if not path.is_file():
        print(f"not a file: {path}", file=sys.stderr)
        return 2
    print("\n".join(scan(path.read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
