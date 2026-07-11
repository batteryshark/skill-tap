# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

RULES = {
    "R-ENG-01": ("CORE_ENGINE", 6), "R-ENG-02": ("CORE_ENGINE", 4),
    "R-ENG-03": ("CORE_ENGINE", 6), "R-ENG-04": ("CORE_ENGINE", 5),
    "R-ENG-05": ("CORE_ENGINE", 5), "R-ENG-06": ("CORE_ENGINE", 4),
    "R-SCR-01": ("SCORING_SPINS", 6), "R-SCR-02": ("SCORING_SPINS", 4),
    "R-SCR-03": ("SCORING_SPINS", 6), "R-SCR-04": ("SCORING_SPINS", 5),
    "R-SCR-05": ("SCORING_SPINS", 4),
    "R-CTL-01": ("CONTROLS_LOCKDOWN", 4), "R-CTL-02": ("CONTROLS_LOCKDOWN", 3),
    "R-CTL-03": ("CONTROLS_LOCKDOWN", 4), "R-CTL-04": ("CONTROLS_LOCKDOWN", 5),
    "R-CTL-05": ("CONTROLS_LOCKDOWN", 4),
    "R-GOV-01": ("GAME_OVER_MODES", 4), "R-GOV-02": ("GAME_OVER_MODES", 3),
    "R-GOV-03": ("GAME_OVER_MODES", 1), "R-GOV-04": ("GAME_OVER_MODES", 2),
    "R-UIE-01": ("UI_EFFECTS", 4), "R-UIE-02": ("UI_EFFECTS", 4),
    "R-UIE-03": ("UI_EFFECTS", 3), "R-UIE-04": ("UI_EFFECTS", 2),
    "R-UIE-05": ("UI_EFFECTS", 2),
}
VALID = {"PASS", "FAIL", "UNKNOWN"}


def template() -> dict:
    return {"strictness": "balanced", "rules": {rule: "UNKNOWN" for rule in RULES}}


def load_statuses(path: Path) -> tuple[str, dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    strictness = str(data.get("strictness", "balanced")).lower()
    if strictness not in {"strict", "balanced"}:
        raise ValueError("strictness must be strict or balanced")
    raw = data.get("rules")
    if not isinstance(raw, dict):
        raise ValueError("rules must be an object mapping every rule ID to PASS, FAIL, or UNKNOWN")
    missing = sorted(set(RULES) - set(raw))
    extra = sorted(set(raw) - set(RULES))
    if missing or extra:
        raise ValueError(f"rule set mismatch; missing={missing}, extra={extra}")
    statuses = {rule: str(status).upper() for rule, status in raw.items()}
    invalid = {rule: status for rule, status in statuses.items() if status not in VALID}
    if invalid:
        raise ValueError(f"invalid statuses: {invalid}")
    return strictness, statuses


def score(strictness: str, statuses: dict[str, str]) -> dict:
    unknown_fraction = 0.2 if strictness == "strict" else 0.4
    earned = defaultdict(float)
    maximum = defaultdict(float)
    counts = defaultdict(lambda: defaultdict(int))
    for rule, (category, weight) in RULES.items():
        status = statuses[rule]
        maximum[category] += weight
        counts[category][status] += 1
        if status == "PASS":
            earned[category] += weight
        elif status == "UNKNOWN":
            earned[category] += weight * unknown_fraction
    total = round(sum(earned.values()), 2)
    unknown_count = sum(1 for status in statuses.values() if status == "UNKNOWN")
    if unknown_count > len(RULES) / 2:
        verdict = "insufficient-evidence"
    else:
        verdict = "high-alignment" if total >= 90 else "moderate-alignment" if total >= 75 else "low-alignment"
    return {
        "strictness": strictness,
        "overall_score": total,
        "verdict": verdict,
        "unknown_rules": unknown_count,
        "unofficial": True,
        "category_scores": [
            {
                "category": category,
                "score": round(earned[category], 2),
                "maximum": int(maximum[category]),
                "status_counts": dict(counts[category]),
            }
            for category in sorted(maximum)
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score an unofficial tetromino baseline audit.")
    sub = parser.add_subparsers(dest="command", required=True)
    emit = sub.add_parser("template", help="Emit a complete UNKNOWN status template.")
    emit.add_argument("--output", type=Path)
    score_parser = sub.add_parser("score", help="Score a completed JSON status file.")
    score_parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "template":
            rendered = json.dumps(template(), indent=2) + "\n"
            if args.output:
                args.output.write_text(rendered, encoding="utf-8")
            else:
                print(rendered, end="")
            return 0
        strictness, statuses = load_statuses(args.input)
        print(json.dumps(score(strictness, statuses), indent=2))
        return 0
    except (OSError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
