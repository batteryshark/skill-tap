---
name: tier-plan
description: Turn one request into a routed work graph — decomposed into units, each assigned a capability tier, a reasoning budget, a verification command, and a dispatch order. Use this before executing large or multi-part work, when asked to "plan this out", "how would you split this up", "what should each model do", "estimate what this will cost", when a job is too big for one context and needs carving up, or when someone wants the delegation plan reviewed before any tokens are spent on execution. Produces a plan document, not the work itself.
---

# Tier plan

The output is a plan document someone can read, argue with, and then hand to an
orchestrator. Producing it separately from execution is what makes the routing
inspectable — a bad plan caught on paper costs nothing, and a bad plan caught
mid-execution costs everything already spent.

Read the tier and budget scorecards in `references/routing.md` before scoring.
This skill applies that rubric rather than restating it, so the scores mean the
same thing to whoever executes the plan.

## 1. Establish the frame

Before decomposing, pin down four things. Getting these wrong makes every
downstream decision wrong in a way the plan will not reveal.

- **The deliverable.** What exists at the end that does not exist now. Not the
  activity — the artifact.
- **The definition of done.** How anyone would confirm it. If this cannot be
  stated for the whole job, that is the most important finding in the plan and
  it belongs at the top, because it means the final unit is unverifiable and has
  to be routed accordingly.
- **What is already decided.** Constraints, prior choices, things not up for
  reconsideration. Unstated, these get relitigated by every unit that touches
  them.
- **The roster.** Which cells are reachable. Read `roster.yaml` if the project
  has one; otherwise note what you assumed, since a plan routed to models that
  do not exist is a fiction.

## 2. Decompose to checkable units

**A unit is the smallest chunk with an independently checkable output.** That
definition does the work — it sets granularity from below (a chunk with no
checkable output is not a unit, it is half of one) and the handoff tax sets it
from above (a chunk smaller than its brief should be merged).

Test each candidate unit:

- Can I write its VERIFY line? If not, either enlarge it until a check exists, or
  mark it unverified and let the tier scorecard route it up.
- Is the work at least twice the brief? If not, merge it into its neighbor.
- Does it need something another unit produces? That is a dependency edge, not a
  reason to merge — merging on dependency is how a plan collapses back into one
  serial blob.

Two decomposition patterns cover most large jobs, and naming which one you are
using clarifies the whole plan:

**Sweep** — many similar items, one shape. Plan one contract template and a batch
size. The risk is a template defect multiplied by the item count, so the plan
should include a pilot: run three, check, then release the rest.

**Funnel** — cheap broad pass narrows to expensive deep pass. Plan the filter
criterion explicitly, and state the expected survivor ratio, because that ratio
is the entire justification for the funnel. If you cannot estimate it, the funnel
may not be worth building.

## 3. Score every unit

Run both scorecards. Record the component scores, not just the verdict — a bare
"T2" cannot be argued with, while `intent 1, blast 0, coupling 1, novelty 0,
verify 0 → 2` can be, and the argument is usually where a plan gets fixed.

Apply the overrides consciously and mark them in the plan. The
unverifiable-and-consequential floor and the verified-and-self-contained drop are
both counterintuitive enough that a reader will assume a mistake unless the plan
says which override fired.

## 4. Build the graph

Draw dependencies. Then extract three things:

- **Waves.** Units with no unmet dependency run together. Wave 1, wave 2, and so
  on. This is the dispatch order.
- **The critical path.** The longest dependency chain. It sets wall-clock, and it
  is usually where the T3 units sit — which means shortening it means finding
  work currently gated on a T3 unit that does not actually need to be.
- **Write conflicts.** Units in the same wave touching the same files. Partition
  them, serialize them, or isolate them. Concurrent edits to one file are the
  most common way a parallel plan produces unusable output.

## 5. Forecast

For each unit: estimated tokens × the cost index of its assigned model, plus the
handoff tax per unit. Sum by tier so the shape is visible.

Then state the counterfactual: what this would cost run entirely at the top tier.
The ratio is the value of the plan, and if it is close to 1 the honest
recommendation is to skip the orchestration and run it straight — which is a
legitimate and useful thing for a planning skill to conclude.

Flag the two or three units where the estimate is least reliable. Those are where
the forecast will break, and naming them up front is more useful than a precise
total that quietly assumes they behave.

## 6. Write the plan

Use `references/plan-template.md`. Keep the routing table dense — one line per unit,
scores visible. The prose sections carry the reasoning; the table carries the
decisions.

## What makes a plan good

**Every unit has a real check, or is explicitly marked as unverified.** The
marked ones are where the risk actually lives, and they should be the first thing
a reviewer's eye lands on.

**The tier distribution is defensible.** Mostly T3 means the decomposition failed
— the work was not carved into pieces that a lower tier could hold. Mostly T1
with a hard problem in it means something is being under-routed and will
escalate. Say which units you are least confident about rather than presenting a
uniform confidence you do not have.

**Failure has somewhere to go.** For each unit, what happens when it fails —
retry, re-brief, escalate, or halt the run. Units whose failure should stop
everything need marking, because the default is to keep going.

**The plan is falsifiable.** A reader should be able to point at a row and say
"that is not T2, that is T3, because coupling is 2 not 1." If they cannot, the
plan is a narrative rather than a plan.

## Tools in this package

`bin/tier-plan` lints a finished plan. It reads the routing table and reports
dependency cycles, units naming a dependency that does not exist, units with no
verification, and the parallel waves the graph actually implies.

```sh
bin/tier-plan plan.md
```

It reports what the table says. Whether a unit is routed correctly is a
judgment the rubric above is for.

Role prompts for the two agents this skill dispatches are in `agents/`.

## Reference

- `references/routing.md` — the tier and budget scorecards, with worked examples
- `references/plan-template.md` — the plan document's shape
- `references/roster.example.yaml` — model roster format

A companion `orchestrate` skill executes the plan this one produces, and a
`model-fitness` skill fills the roster. Neither is required.
