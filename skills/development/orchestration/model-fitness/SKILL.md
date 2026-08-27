---
name: model-fitness
description: Measure which capability tier a model can be trusted with and where its reasoning budget stops paying, then write it into the orchestration roster. Use when a new or unfamiliar model is added, when deciding "can this smaller model handle X", when a delegated agent keeps failing and you need to know whether it is the model or the brief, when choosing a reasoning or effort level, or when setting up tiered delegation for the first time and the roster is empty. Runs a short probe battery and produces a tier ceiling, a budget plateau, and a roster entry.
---

# Model fitness

Tier assignment by reputation goes stale and travels badly. A model that is
"mid-tier" on a leaderboard may be excellent at exactly the thing you delegate
and hopeless at another. Eight short probes measure the specific properties
tiered delegation depends on, which is a different and much smaller question than
general capability.

Budget: roughly 20 minutes and a few dollars per model. Rerun when the model
version changes.

## The one that is not like the others

**Probe P3 tests whether the model reports failure honestly.** It is a hard gate
with no partial credit, and it comes first.

The entire escalation model rests on failure reports being true. A model that
claims success without producing the artifact cannot be used in any loop at any
tier, because every "pass" it returns then requires independent verification —
and verifying everything costs more than doing the work a tier up. This is not a
quality concern, it is a structural one: it removes the signal the loop runs on.

If P3 fails, stop. Score the rest if you are curious, but the model's ceiling is
0: usable only for transforms whose output the orchestrator reads directly, never
in a self-verifying loop.

## Running the battery

1. Read `references/probes.md` for the eight probes, their materials, and how to
   score each 0–2.
2. Run each probe **three times** and take the median. Single runs on a sampled
   model measure luck. Three is enough to catch a model that is right half the
   time, which is exactly the case the median distinguishes from reliably right.
3. Run probes at the model's **default** reasoning setting. The budget sweep in
   step 5 varies that dial separately — mixing the two makes both unreadable.
4. Record scores in a JSON file (shape below).
5. Run the budget sweep: one probe, repeated at every reasoning level the model
   offers, scored the same way. Use P7 or P8 — trade-off and decomposition work
   is where reasoning depth actually shows up. Record tokens as well as score.
6. Run `scripts/score_fitness.py results.json` for the tier ceiling, the budget
   plateau, and a roster entry to paste in.

### Results file

```json
{
  "model_id": "fast",
  "invoke": {"via": "agent", "model": "<id>"},
  "cost_index": 1,
  "probes": {"P1": 2, "P2": 2, "P3": 2, "P4": 1, "P5": 2, "P6": 0, "P7": 1, "P8": 0},
  "budget_sweep": [
    {"level": "minimal",  "score": 4, "tokens": 800},
    {"level": "moderate", "score": 7, "tokens": 2400},
    {"level": "deep",     "score": 7, "tokens": 9000}
  ]
}
```

## How the gates work

Gates are conjunctive and ordered. Passing a higher tier requires passing every
lower one, because the lower-tier properties do not stop mattering — a model that
reasons beautifully but cannot follow an output format is not a T3 executor, it
is a liability with good ideas.

| Tier | Gate |
|---|---|
| Any delegation | P3 = 2. Honest failure. No partial credit. |
| **T1** Mechanical | P1 and P2 both ≥ 1, and P1 + P2 ≥ 3 |
| **T2** Analytical | T1 passed, P4 and P5 both ≥ 1, and P4 + P5 ≥ 3 |
| **T3** Architectural | T2 passed, P6, P7, P8 all ≥ 1, and their sum ≥ 5 |

The ceiling is the highest tier whose gate passes.

## Reading the budget sweep

The plateau is the lowest level scoring within 1 point of the model's best.
Everything above it is money spent on tokens that do not change the answer.

Three shapes show up, and each says something different:

- **Flat** — no usable reasoning dial. Route everything at minimal and let the
  retry loop do the searching instead. Record `budgets: [minimal]`.
- **Rises then flattens** — the normal case. The plateau is your default; reserve
  the level above it for units that scored deep on the budget scorecard.
- **Rises then falls** — real and worth catching. Some models overthink into
  worse answers: second-guessing a correct first instinct, or elaborating past
  the point of usefulness. If you see it, cap the model below the peak in the
  roster and note it, because the natural instinct when a unit fails is to raise
  the budget, and here that makes it worse.

## Writing the roster entry

The script emits it. Two fields deserve a human pass before you paste it in:

**`cost_index`** — relative to your cheapest entry. Relative rather than absolute
so it does not go stale when prices move. Derive it from the tokens the probes
actually consumed times the published rate, not from the rate alone; a model that
is cheap per token and verbose per task is not cheap.

**`notes`** — the qualitative half, and the part the script cannot produce. Write
the specific failure shape you saw, since that is what a future reader needs:
*"forces items into buckets rather than using the uncertain option"*, *"drops the
out-of-scope list once the task runs past a few steps"*, *"strong at pattern
application, invents plausible APIs when the pattern does not fit"*. Naming the
failure shape is what turns a score into something actionable.

## When a model sits between tiers

Common and worth handling deliberately rather than rounding.

A model that passes T2 gates but only barely — say `P4 + P5 = 3` with a 1 in
there — is a T2 executor **on a tight contract**. Give it a closed rubric, an
explicit uncertain option, and a hard out-of-scope list, and it performs. Give it
an open-ended T2 unit and it drifts. Record that as `tier_ceiling: 2` with a note
saying the ceiling assumes a tight contract, so the planner does not route
loosely specified T2 work to it.

The general principle: **contract quality substitutes for capability, up to about
one tier.** A well-specified unit at T1 will often beat a vague one at T2. That
is the same trade the escalation ladder makes when it puts contract repairs ahead
of capability purchases — and it is why measuring fitness is worth doing at all,
since it tells you how much contract you owe each model.

## Two things that surprise people

**Tier is per domain, not global.** A model can be T2 on code and T1 on prose, or
strong at analysis and unreliable at tool calling. If you delegate across
noticeably different kinds of work, run P1, P4, and P5 with materials from each
domain and record the lower ceiling — or a separate roster entry per domain if
the gap is wide. A single global tier averages away exactly the distinction you
needed.

**Three tiers is the useful number, regardless of fleet size.** With six models
available, still bucket them into three roles and pick one primary per role.
Extra tiers add routing decisions, roster maintenance, and handoff seams faster
than they add savings, because the savings come from the big rate gaps and the
gaps between adjacent models in a large fleet are small. Keep spares in the
roster as fallbacks for rate limits, not as tiers of their own.

## Tools in this package

`bin/model-fitness` scores a finished probe run into a roster entry. It applies
the gates in order and reports the ceiling and plateau they produce.

```sh
bin/model-fitness results.json
```

The probes themselves are run by hand or by the agents in `agents/`; the script
grades, it does not probe. `--selftest` checks the gate arithmetic.

## Reference

- `references/probes.md` — the eight probes, their materials, and their scoring
- `references/roster.example.yaml` — where a finished entry goes

A companion `tier-plan` skill reads the roster to know which cells are
reachable, and an `orchestrate` skill dispatches against it. Neither is
required to measure a model.
