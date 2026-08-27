# Routing: picking the cell

Two scorecards. Run both per work unit. They are independent — score tier without
thinking about budget, then budget without revisiting tier.

The reason to score rather than eyeball: eyeballing has a systematic bias toward
over-assignment. Every task feels like it needs the smart model when you are the
smart model looking at it. Counting signals corrects for that.

---

## Scorecard 1: tier

Score each 0, 1, or 2.

**Intent gap** — how much of "what good looks like" is unstated?
- 0 — The target is fully specified. Someone could diff the result against a description.
- 1 — The shape is given, the details are inferred.
- 2 — The executor has to work out what the user actually wants.

**Blast radius** — cost of a wrong answer that ships undetected?
- 0 — Trivially reverted, caught immediately, or throwaway.
- 1 — Costs rework downstream.
- 2 — Silent data corruption, security, money, or user-facing damage.

**Coupling** — how many other things must the output stay consistent with?
- 0 — Self-contained. One file, one function, one record.
- 1 — A handful of known call sites or a defined interface.
- 2 — Cross-module invariants, or consistency with other agents' concurrent output.

**Novelty** — how far from a stated or well-known pattern?
- 0 — Pure application of a pattern given in the brief.
- 1 — Common pattern the executor is expected to know.
- 2 — No template exists; the approach has to be invented.

**Verification** (this one subtracts) — how strong is the machine check?
- 0 — No check. Correctness is a matter of reading it.
- 1 — Partial. It compiles, lints, or type-checks, but semantics are unverified.
- 2 — Strong. A test, a golden file, an exit code, or a differential comparison
  that actually fails when the work is wrong.

```
tier_score = intent + blast + coupling + novelty − verification
```

| Score | Tier |
|---|---|
| ≤ 1 | T1 Mechanical |
| 2–4 | T2 Analytical |
| ≥ 5 | T3 Architectural |

### Two overrides

**Unverifiable and consequential → T3 floor.** If `blast == 2` and
`verification == 0`, route T3 regardless of score. You cannot retry your way out
of a task where a confident wrong answer is both undetectable and expensive. The
only defense left is the executor being right the first time.

**Strongly verified and self-contained → T1 is fine even at high novelty.** If
`verification == 2`, `intent == 0`, and `coupling == 0`, the retry loop performs
the search. Novelty stops mattering when the executor can try, fail visibly, and
try again. This is why a cheap model can brute-force an undocumented binary
format that would otherwise look like T3 work.

### Verification is a lever, not a fact

The other four signals describe the task. Verification describes what you have
built around it — which means it is the one you can change.

The cheapest available check sets the floor:

| Cheapest available check | Lowest safe tier |
|---|---|
| Deterministic — exit code, diff against golden file, schema validation, test | T1 |
| Rubric — closed criteria a bounded reviewer can apply | T2 |
| Judgment only — taste, architecture, threat modeling | T3 |

So before routing a unit up, ask: **what small artifact would make this
self-checking?** A test, a golden file, a schema, a differential comparison
against a known-good implementation. Ten minutes of top-tier effort building one
converts a judgment task into a deterministic one, and every attempt after that —
including every retry — runs at the bottom rate. On a sweep of forty units, that
one artifact is usually the largest single saving available.

This is also the reason the tier scores in a plan should be recorded *after* you
have decided what checks to build. Scoring the task as you found it routes work up
that a small investment would have routed down.

**One hard limit: a model never grades its own judgment.** Deterministic
self-checks are fine — the test suite is the grader, not the model. But anything
judged by rubric or taste needs different eyes: the orchestrator, or a reviewer
briefed separately so it has not already committed to the answer. A model asked
to grade its own reasoning will nearly always ratify it, so that check reads as
verification while providing none.

---

## Scorecard 2: reasoning budget

Score each 0, 1, or 2.

**Branch factor** — how many plausible approaches present themselves?
- 0 — One obvious path.
- 1 — Two or three, easy to compare.
- 2 — Wide or unknown; the space has to be explored to be seen.

**Backtrack cost** — what does a wrong turn cost?
- 0 — Cheap and instant to test and revert.
- 1 — Slow to test, or partially destructive.
- 2 — Irreversible, or the wrongness is not observable.

**Simultaneous constraints** — how many must hold at once in the answer?
- 0 — Two or fewer.
- 1 — Three to five.
- 2 — More than five, or they conflict and must be traded off.

```
budget_score = branch + backtrack + constraints
```

| Score | Budget |
|---|---|
| 0–1 | Minimal |
| 2–3 | Moderate |
| 4–6 | Deep |

### The crossover rule

This is the highest-leverage adjustment in the whole framework, so it is worth
stating the mechanism rather than just the rule.

Reasoning and iteration are substitutes. Both are ways of searching a solution
space; they differ in what they cost and what they need. Reasoning searches
internally, costs output tokens, and needs nothing from the environment.
Iteration searches externally, costs a round trip per step, and needs a check
that tells you when you have landed.

So the choice is set by whether a check exists:

- **`backtrack == 0` and `verification == 2` → drop one budget level, add one
  retry.** The environment will do the search for free. Paying for deep reasoning
  in front of a fast reliable test is buying something you are about to be given.
- **`verification == 0` → add one budget level.** There is no second shot. The
  entire search has to happen before the answer is emitted, so it has to happen
  internally.

The failure this prevents is expensive in both directions: deep reasoning on a
tight test loop wastes tokens, and minimal reasoning on an unverifiable call
ships a confident guess.

---

## The grid

Where the common cells land, and what they are for.

| | Minimal | Moderate | Deep |
|---|---|---|---|
| **T1** | Bulk transforms, scaffolding, defined procedures | Script-and-debug loops, syntax fixing to green | Narrow combinatorial puzzles with a hard check — parsers, format reversing, constraint solving |
| **T2** | High-volume classification, extraction, triage against a rubric | Log analysis, drafting to spec, decompiled-logic summaries | Correlating many findings into a small set of root causes |
| **T3** | Taste and recall calls — is this idiomatic, is this the right library, does this smell wrong | Design review, moderate root-cause | Planning, cross-cutting synthesis, obscure root-cause, conflicting-constraint architecture |

Two cells earn special attention because they are the ones routinely gotten wrong:

**(T1, deep)** is usually better value than (T3, minimal) for anything that is
narrow, checkable, and hard. The cheap model with room to think and a test to
land on will out-price the expensive model every time, provided the problem
genuinely fits in its head.

**(T3, minimal)** is real and underused. Judgment calls that need breadth of
knowledge but no search — naming, library selection, "is this API idiomatic",
"does this design have a smell" — want the big model answering quickly. Deep
reasoning on a recall question buys nothing but latency.

---

## Worked examples

| Unit | I | B | C | N | V | Score | Route |
|---|---|---|---|---|---|---|---|
| Rename a symbol repo-wide, tests must pass | 0 | 1 | 1 | 0 | 2 | 0 | T1 / minimal |
| Parse hex offsets from an undocumented ROM header | 1 | 0 | 0 | 2 | 2 | 1 | T1 / deep (override 2) |
| Categorize 400 crash logs against a given rubric | 1 | 0 | 1 | 0 | 0 | 2 | T2 / minimal |
| Summarize what a decompiled function does | 1 | 0 | 1 | 1 | 0 | 3 | T2 / moderate |
| Reconcile 6 agents' findings into one root cause | 1 | 1 | 2 | 1 | 0 | 5 | T3 / deep |
| Why does this only fail on ARM under load | 2 | 1 | 2 | 2 | 1 | 6 | T3 / deep |
| Pick the auth library for a new service | 2 | 2 | 1 | 0 | 0 | 5 | T3 / minimal |
| Add the null check the ticket specifies | 0 | 1 | 0 | 0 | 2 | −1 | T1 / minimal |
| Rotate a production credential across 9 services | 0 | 2 | 2 | 0 | 0 | 4 → T3 | T3 (blast+unverified override) |

The last row is the override doing its job. By raw score it is T2 work — the
steps are all specified. But nothing checks it and getting it wrong takes
production down, so it goes up.

---

## Mapping cells to your roster

The grid is abstract. `assets/roster.example.yaml` is where it meets the models
you actually have: each roster entry declares a tier ceiling, the budget levels
it supports, and a relative cost index.

Route to **the cheapest roster entry whose tier ceiling meets the required tier**
and which supports the required budget. Ceiling, not match — a T3-capable model
running a T1 unit is fine and sometimes correct (see the merge rule in
`economics.md`), it is just usually wasteful.

When the roster has one entry, tier collapses and only the budget dial remains.
That is a perfectly usable degenerate case: budget control plus contract
discipline plus the escalation ladder still captures most of the value, because
most of the value was never in the model switching.
