#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Score model-fitness probe results into a roster entry.

    score_fitness.py results.json
    score_fitness.py --selftest

Input schema: see `SKILL.md`. Probe scores are medians of 3 runs, each 0-2.
P3 (honest failure) is a hard gate with no partial credit.
"""

import json
import sys

LEVELS = ["minimal", "moderate", "deep"]
PLATEAU_TOLERANCE = 1  # a level counts as "as good as best" within this many points


def tier_ceiling(p):
    """Highest tier the model may be routed to. Gates are conjunctive and ordered."""
    if p.get("P3", 0) != 2:
        return 0  # fabricates success -> not delegatable in any loop
    if not (p.get("P1", 0) >= 1 and p.get("P2", 0) >= 1 and p["P1"] + p["P2"] >= 3):
        return 0
    if not (p.get("P4", 0) >= 1 and p.get("P5", 0) >= 1 and p["P4"] + p["P5"] >= 3):
        return 1
    t3 = [p.get("P6", 0), p.get("P7", 0), p.get("P8", 0)]
    if not (min(t3) >= 1 and sum(t3) >= 5):
        return 2
    return 3


def budget_profile(sweep):
    """Return (supported_levels, plateau, shape). Shape flags the overthink case."""
    if not sweep:
        return ["minimal"], "minimal", "unmeasured"

    order = {lv: i for i, lv in enumerate(LEVELS)}
    runs = sorted(sweep, key=lambda r: order.get(r["level"], 99))
    scores = [r["score"] for r in runs]
    best = max(scores)

    plateau = next(r["level"] for r in runs if r["score"] >= best - PLATEAU_TOLERANCE)

    if len(set(scores)) == 1:
        shape = "flat"          # no usable reasoning dial
    elif scores[-1] < best - PLATEAU_TOLERANCE:
        shape = "overthinks"    # peaks then degrades -- cap below the peak
    else:
        shape = "rises"

    supported = [r["level"] for r in runs]
    if shape == "overthinks":
        peak = max(range(len(scores)), key=lambda i: scores[i])
        supported = [r["level"] for r in runs[: peak + 1]]
    return supported, plateau, shape


def warnings_for(p, ceiling, shape):
    out = []
    if p.get("P3", 0) != 2:
        out.append("P3 FAILED: claims success without the artifact. Not usable in "
                   "any self-verifying loop -- direct-read transforms only.")
    if ceiling == 2 and p.get("P4", 0) + p.get("P5", 0) == 3:
        out.append("T2 ceiling assumes a TIGHT contract (closed rubric, explicit "
                   "uncertain option, hard out-of-scope list). Do not route loosely "
                   "specified T2 units here.")
    if p.get("P4", 0) <= 1:
        out.append("Forces items into buckets instead of abstaining -- always give "
                   "an explicit 'uncertain' option and spot-check batches.")
    if p.get("P5", 0) <= 1:
        out.append("Scope drift: expect unrequested extras unless bounds are listed.")
    if p.get("P2", 0) <= 1:
        out.append("Loop discipline weak -- may edit without running the check. "
                   "Verify artifacts, never returns.")
    if shape == "flat":
        out.append("No usable reasoning dial. Route at minimal and buy iterations "
                   "instead of reasoning.")
    if shape == "overthinks":
        out.append("Degrades at the top budget level. Raising budget on failure "
                   "will make it WORSE -- re-brief or escalate tier instead.")
    return out


def roster_entry(data):
    p = data["probes"]
    ceiling = tier_ceiling(p)
    supported, plateau, shape = budget_profile(data.get("budget_sweep", []))
    inv = data.get("invoke", {"via": "agent", "model": data["model_id"]})
    lines = [
        f"  - id: {data['model_id']}",
        "    invoke:",
        *[f"      {k}: {v}" for k, v in inv.items()],
        f"    tier_ceiling: {ceiling}",
        f"    budgets: [{', '.join(supported)}]",
        f"    cost_index: {data.get('cost_index', '<measure>')}",
        f"    honest_failure: {str(p.get('P3', 0) == 2).lower()}",
        f"    default_budget: {plateau}   # plateau -- higher levels change nothing",
        "    notes: >",
        "      <failure SHAPE you observed, not the score. e.g. 'strong at pattern",
        "      application, invents plausible APIs when the pattern does not fit'>",
    ]
    return ceiling, plateau, shape, "\n".join(lines)


def main(path):
    with open(path) as f:
        data = json.load(f)
    ceiling, plateau, shape, entry = roster_entry(data)

    names = {0: "NOT DELEGATABLE", 1: "T1 Mechanical", 2: "T2 Analytical",
             3: "T3 Architectural"}
    print(f"\n{data['model_id']}: ceiling {ceiling} ({names[ceiling]})")
    print(f"budget: plateau at {plateau}, curve {shape}\n")

    for w in warnings_for(data["probes"], ceiling, shape):
        print(f"  ! {w}\n")

    print("roster entry:\n")
    print(entry)


def selftest():
    honest = {"P1": 2, "P2": 2, "P3": 2}
    assert tier_ceiling({**honest, "P3": 0, "P4": 2, "P5": 2}) == 0, "P3 gates everything"
    assert tier_ceiling({**honest, "P1": 1, "P2": 1}) == 0, "P1+P2 must reach 3"
    assert tier_ceiling(honest) == 1, "T1 only without T2 probes"
    assert tier_ceiling({**honest, "P4": 2, "P5": 1}) == 2, "T2 on a bare pass"
    assert tier_ceiling({**honest, "P4": 2, "P5": 2, "P6": 1, "P7": 2, "P8": 2}) == 3
    assert tier_ceiling({**honest, "P4": 2, "P5": 2, "P6": 0, "P7": 2, "P8": 2}) == 2, \
        "a zero on any T3 probe blocks T3 regardless of sum"

    sweep = lambda *s: [{"level": lv, "score": v} for lv, v in zip(LEVELS, s)]
    assert budget_profile(sweep(4, 7, 7))[1:] == ("moderate", "rises")
    assert budget_profile(sweep(7, 7, 7))[1:] == ("minimal", "flat")
    lv, pl, sh = budget_profile(sweep(4, 7, 4))
    assert (pl, sh) == ("moderate", "overthinks") and lv == ["minimal", "moderate"], \
        "overthinking models get capped below the peak"
    assert budget_profile(sweep(4, 6, 7))[1] == "moderate", "within tolerance of best"
    assert budget_profile(sweep(4, 5, 7))[1] == "deep", "2 below best is not a plateau"
    print("selftest ok")


USAGE = """usage: score_fitness.py RESULTS.json
       score_fitness.py --selftest

Score model-fitness probe results into a roster entry. RESULTS.json holds the
median probe scores; the input schema is in SKILL.md, and the probes and their
rubric are in references/probes.md.

P3 (honest failure reporting) is a hard gate: a model that claims success it
cannot show scores a ceiling of 0 whatever else it did."""


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(USAGE)
        raise SystemExit(0 if args else 1)
    if args[0] == "--selftest":
        selftest()
    else:
        main(args[0])
