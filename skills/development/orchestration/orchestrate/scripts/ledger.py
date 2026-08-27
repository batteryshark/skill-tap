#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Budget ledger for a delegated run.

    ledger.py record --unit u3 --event dispatch --tier 1 --tokens 12000
    ledger.py record --unit u3 --event escalate --note "missing fixture path"
    ledger.py report
    ledger.py --selftest

Events append to a JSONL file (default `.orchestrate-ledger.jsonl`, override
with --ledger or ORCHESTRATE_LEDGER). The report states what was spent, where
it went, and which units are at the escalation cap. It reports evidence: the
routing calls stay with whoever reads it.
"""

import argparse
import json
import os
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

EVENTS = ("dispatch", "return", "escalate", "abandon")
ESCALATION_CAP = 2  # a unit escalated twice is a plan problem, not a routing one
DEFAULT_LEDGER = ".orchestrate-ledger.jsonl"


def ledger_path(explicit: str | None) -> Path:
    return Path(explicit or os.environ.get("ORCHESTRATE_LEDGER", DEFAULT_LEDGER))


def read(path: Path) -> list[dict]:
    """Every readable record. A malformed line is skipped, not fatal: a ledger
    is a running log, and one bad append must not hide the rest."""
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("unit") and row.get("event") in EVENTS:
            rows.append(row)
    return rows


def record(path: Path, row: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def summarize(rows: list[dict]) -> dict:
    """Per-unit totals plus the two facts worth acting on: units still open,
    and units at the escalation cap."""
    units: dict[str, dict] = defaultdict(
        lambda: {"dispatches": 0, "returns": 0, "escalations": 0,
                 "abandoned": False, "tokens": 0, "tiers": [], "notes": []})
    for row in rows:
        unit = units[str(row["unit"])]
        event = row["event"]
        if event == "dispatch":
            unit["dispatches"] += 1
            tier = row.get("tier")
            if isinstance(tier, int):
                unit["tiers"].append(tier)
        elif event == "return":
            unit["returns"] += 1
        elif event == "escalate":
            unit["escalations"] += 1
        elif event == "abandon":
            unit["abandoned"] = True
        tokens = row.get("tokens")
        if isinstance(tokens, (int, float)) and not isinstance(tokens, bool):
            unit["tokens"] += int(tokens)
        note = row.get("note")
        if note:
            unit["notes"].append(f"{event}: {note}")
    return dict(units)


def render(units: dict) -> str:
    if not units:
        return "No events recorded yet."
    lines = [f"{'unit':<16} {'disp':>4} {'ret':>4} {'esc':>4} {'tokens':>10}  tier",
             "-" * 52]
    total = 0
    for name in sorted(units):
        u = units[name]
        total += u["tokens"]
        tiers = "→".join(f"T{t}" for t in u["tiers"]) or "—"
        lines.append(f"{name:<16} {u['dispatches']:>4} {u['returns']:>4} "
                     f"{u['escalations']:>4} {u['tokens']:>10,}  {tiers}")
    lines.append("-" * 52)
    lines.append(f"{'total':<16} {'':>4} {'':>4} {'':>4} {total:>10,}")

    capped = [n for n, u in units.items() if u["escalations"] >= ESCALATION_CAP]
    if capped:
        lines += ["", f"At the escalation cap ({ESCALATION_CAP}): "
                      + ", ".join(sorted(capped)),
                  "  A unit escalated this often is not a routing problem. Stop,",
                  "  surface what was tried, and ask."]
    open_units = [n for n, u in units.items()
                  if u["dispatches"] > u["returns"] and not u["abandoned"]]
    if open_units:
        lines += ["", "Dispatched and not returned: " + ", ".join(sorted(open_units))]
    notes = [(n, note) for n in sorted(units) for note in units[n]["notes"]]
    if notes:
        lines += ["", "Notes:"] + [f"  {n}: {note}" for n, note in notes]
    return "\n".join(lines)


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "ledger.jsonl"
        for row in (
            {"unit": "u1", "event": "dispatch", "tier": 1, "tokens": 100},
            {"unit": "u1", "event": "return", "tokens": 50},
            {"unit": "u2", "event": "dispatch", "tier": 1, "tokens": 200},
            {"unit": "u2", "event": "escalate", "note": "no fixture"},
            {"unit": "u2", "event": "dispatch", "tier": 2, "tokens": 400},
            {"unit": "u2", "event": "escalate", "note": "still failing"},
        ):
            record(path, row)
        path.open("a").write("not json\n")  # a bad line must not hide the rest

        units = summarize(read(path))
        assert units["u1"]["tokens"] == 150, units["u1"]
        assert units["u2"]["escalations"] == 2, units["u2"]
        assert units["u2"]["tiers"] == [1, 2], units["u2"]
        out = render(units)
        assert "At the escalation cap" in out and "u2" in out
        assert "Dispatched and not returned: u2" in out, out
        assert "u1" not in out.split("Dispatched and not returned:")[1]
        assert render({}) == "No events recorded yet."
    print("selftest ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", help=f"default: {DEFAULT_LEDGER}")
    parser.add_argument("--selftest", action="store_true",
                        help="run the built-in checks and exit")
    sub = parser.add_subparsers(dest="command")

    add = sub.add_parser("record", help="append one event")
    add.add_argument("--unit", required=True)
    add.add_argument("--event", required=True, choices=EVENTS)
    add.add_argument("--tier", type=int)
    add.add_argument("--tokens", type=int)
    add.add_argument("--note")

    sub.add_parser("report", help="print the ledger")

    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    path = ledger_path(args.ledger)
    if args.command == "record":
        row = {"unit": args.unit, "event": args.event}
        for key in ("tier", "tokens", "note"):
            if getattr(args, key) is not None:
                row[key] = getattr(args, key)
        record(path, row)
        print(f"recorded {args.event} for {args.unit} in {path}")
        return 0
    if args.command == "report":
        print(render(summarize(read(path))))
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
