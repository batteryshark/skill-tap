#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Lint a routing plan's table before anyone executes it.

    plan_lint.py plan.md
    plan_lint.py --selftest

Reads the markdown routing table described in `references/plan-template.md`
and reports what the table says: dependency cycles, dependencies naming a unit
that does not exist, units with no verification, and the parallel waves the
graph actually implies. Whether a unit is routed to the right cell is a
judgment; this reports structure, not routing.
"""

import argparse
import sys
import tempfile
from pathlib import Path

HEADER_CELLS = {"unit", "deps"}
NONE_MARKERS = {"", "—", "-", "--", "none", "n/a", "na", "tbd", "?"}


def split_row(line: str) -> list[str]:
    line = line.strip()
    if not line.startswith("|"):
        return []
    return [cell.strip() for cell in line.strip("|").split("|")]


def parse(text: str) -> list[dict]:
    """Units from the first table carrying both a Unit and a Deps column.

    A plan is prose with a table in it, so the table is found by its columns
    rather than by position: a plan that grew a section above the table still
    lints.
    """
    lines = text.splitlines()
    units: list[dict] = []
    columns: dict[str, int] | None = None
    for line in lines:
        cells = split_row(line)
        if not cells:
            if columns is not None and units:
                break  # the table ended
            continue
        lowered = [c.lower() for c in cells]
        if columns is None:
            if HEADER_CELLS <= set(lowered):
                columns = {name: i for i, name in enumerate(lowered)}
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue  # the header rule
        get = lambda key: (cells[columns[key]]
                           if key in columns and columns[key] < len(cells) else "")
        number = get("#") or str(len(units) + 1)
        name = get("unit")
        if not name and not get("deps"):
            continue  # a blank template row
        units.append({
            "id": number.strip(),
            "name": name,
            "deps": [d.strip() for d in get("deps").replace(",", " ").split()
                     if d.strip().lower() not in NONE_MARKERS],
            "verify": get("verify"),
            "tier": get("tier"),
        })
    return units


def waves(units: list[dict]) -> tuple[list[list[str]], list[str]]:
    """Parallel waves, plus whatever a cycle left unplaceable."""
    pending = {u["id"]: set(u["deps"]) for u in units}
    known = set(pending)
    placed: set[str] = set()
    out: list[list[str]] = []
    while pending:
        ready = sorted(uid for uid, deps in pending.items()
                       if not (deps & known - placed))
        if not ready:
            return out, sorted(pending)
        out.append(ready)
        placed.update(ready)
        for uid in ready:
            del pending[uid]
    return out, []


def findings(units: list[dict]) -> list[str]:
    out: list[str] = []
    if not units:
        return ["no routing table found — is this a plan document?"]
    known = {u["id"] for u in units}
    seen: set[str] = set()
    for unit in units:
        if unit["id"] in seen:
            out.append(f"unit {unit['id']}: duplicate unit number")
        seen.add(unit["id"])
        for dep in unit["deps"]:
            if dep not in known:
                out.append(f"unit {unit['id']}: depends on {dep}, which is not a unit")
        if dep_self := [d for d in unit["deps"] if d == unit["id"]]:
            out.append(f"unit {unit['id']}: depends on itself")
        if unit["verify"].strip().lower() in NONE_MARKERS:
            out.append(f"unit {unit['id']} ({unit['name'] or 'unnamed'}): "
                       "no verification — later units build on an unchecked result")
        if not unit["name"]:
            out.append(f"unit {unit['id']}: no description")
    _, stuck = waves(units)
    if stuck:
        out.append("dependency cycle among units: " + ", ".join(stuck))
    return out


def render(units: list[dict]) -> str:
    lines = [f"{len(units)} unit(s)."]
    order, stuck = waves(units)
    if order:
        lines.append("")
        lines.append("Waves (units that can run together):")
        for i, wave in enumerate(order, 1):
            lines.append(f"  {i}. " + ", ".join(wave))
        widest = max(len(w) for w in order)
        if widest == 1 and len(order) > 1:
            lines.append("  Every wave holds one unit: this graph is a chain, "
                         "and the parallelism is imaginary.")
    problems = findings(units)
    lines.append("")
    if problems:
        lines.append("Findings:")
        lines += [f"  - {p}" for p in problems]
    else:
        lines.append("No structural findings. Routing is still a judgment call.")
    return "\n".join(lines)


SAMPLE = """# Plan: sample

| # | Unit | Deps | Tier | Verify |
|---|---|---|---|---|
| 1 | read the fixtures | — | T1 | `pytest tests/read.py` |
| 2 | port the parser | 1 | T2 | `pytest tests/parse.py` |
| 3 | port the writer | 1 | T2 | `pytest tests/write.py` |
| 4 | reconcile | 2 3 | T3 | — |
"""


def selftest() -> int:
    units = parse(SAMPLE)
    assert [u["id"] for u in units] == ["1", "2", "3", "4"], units
    assert units[3]["deps"] == ["2", "3"], units[3]
    order, stuck = waves(units)
    assert order == [["1"], ["2", "3"], ["4"]], order
    assert stuck == []
    problems = findings(units)
    assert any("unit 4" in p and "no verification" in p for p in problems), problems
    assert not any("unit 2" in p for p in problems), problems

    cycle = parse(SAMPLE.replace("| 1 | read the fixtures | — |",
                                 "| 1 | read the fixtures | 4 |"))
    _, stuck = waves(cycle)
    assert stuck == ["1", "2", "3", "4"], stuck
    assert any("cycle" in p for p in findings(cycle))

    missing = parse("| # | Unit | Deps |\n|---|---|---|\n| 1 | a | 9 |\n")
    assert any("not a unit" in p for p in findings(missing))
    assert findings([])[0].startswith("no routing table")

    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "plan.md"
        path.write_text(SAMPLE)
        assert "Waves" in render(parse(path.read_text()))
    print("selftest ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("plan", nargs="?", help="the plan document")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.plan:
        parser.print_help()
        return 1
    path = Path(args.plan)
    if not path.is_file():
        print(f"no such plan: {path}", file=sys.stderr)
        return 1
    units = parse(path.read_text(encoding="utf-8"))
    print(render(units))
    return 1 if findings(units) and not units else 0


if __name__ == "__main__":
    raise SystemExit(main())
