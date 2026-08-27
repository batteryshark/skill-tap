---
name: orchestrate
description: Route multi-part work across model tiers and reasoning budgets for the best quality-per-token. Use this whenever a request has several separable pieces, when work will be delegated to subagents or other models, when deciding which model or how much thinking a piece of work deserves, when a job is large enough that doing it all at the top tier would be wasteful, or when a cheaper agent keeps failing and you need to decide whether to retry, re-brief, or escalate. Trigger on migrations, audits, sweeps, reverse-engineering campaigns, batch refactors, multi-file analysis, "fan this out", "use subagents", "which model should do this", "make this cheaper", "parallelize this", or any plan where one context cannot hold the whole job.
---

# Orchestrate

Delegation is an economic decision, not a hierarchy. Every hop down a tier buys
cheaper tokens and pays a handoff tax. Every hop up buys reliability and pays
rate. The job here is to place each piece of work in the cell where expected
total cost — including the retries and escalations you will actually incur — is
lowest at acceptable quality.

## First, check the floor

Orchestration has real overhead: writing contracts, re-loading context, grading
returns. Below a certain size it costs more than it saves.

Skip orchestration and just do the work when **any** of these hold:
- The whole job fits comfortably in one delegation with no internal handoff.
- The pieces are not separable — every part needs the same context as every other part.
- Total work is smaller than the briefs required to describe it.

The tell is the brief-to-work ratio. If describing a piece takes nearly as many
tokens as doing it, the piece should not be delegated. Merge it upward.

## The two dials

**Tier** — what the executor must understand.

| Tier | Understands | Typical work |
|---|---|---|
| T1 Mechanical | Nothing unstated. Applies a specified transform. | Syntax translation, scaffolding, running a defined procedure, bulk edits, script-and-loop-until-exit-0 |
| T2 Analytical | Judgment inside a frame someone else set. | Classification against a rubric, log triage, summarizing decompiled logic, drafting to a spec |
| T3 Architectural | Sets the frame. Holds cross-cutting state. | Planning, root-cause on obscure bugs, trade-off calls, synthesizing conflicting agent output |

**Budget** — how much the executor must search before committing. Minimal,
moderate, or deep. Independent of tier: `(T3, minimal)` is a real and useful cell
(a breadth-of-knowledge judgment call with one obvious answer path), and so is
`(T1, deep)` (a narrow puzzle with a wide branch factor).

Score both with the rubric in `references/routing.md`. It is a short scorecard
with worked examples; use it rather than guessing, because the failure mode of
eyeballing tier is systematic over-assignment — everything feels like it needs
the big model until you count the actual signals.

## The loop

**1. Plan.** Decompose into work units. A unit is the smallest chunk with an
independently checkable output. Too fine and handoff tax dominates; too coarse
and you cannot route it. Build the dependency graph so you know what runs in
parallel and what gates wall-clock. Delegate this step to a planning skill if the request is large, or run the
rubric inline if it is a handful of units.

**2. Contract.** For each unit, write the delegation brief. Under-specification
is the single largest source of failure at every tier, and it is invisible until
the return comes back wrong. `references/delegation-contract.md` has the template
and the reasoning behind each field. The non-negotiable parts are the exact
verification command, the pass/fail state, and the out-of-scope list.

**3. Dispatch.** Fan out everything with no unmet dependency, in one batch.
`references/execution.md` covers the mechanics — subagents, model overrides,
external models, and when a workflow engine is warranted.

**4. Verify.** Trust artifacts, never reports. A returned "done, all tests pass"
is a claim, not evidence. Read the artifact or the check output. Models that
fabricate success are the reason `model-fitness` gates on honesty before anything
else — but even honest models drift, and reading the artifact costs less than
inheriting a wrong one into synthesis. Deterministic self-checks are fine to
delegate, since the test is the grader; anything judged by rubric or taste goes
to different eyes, because a model asked to grade its own reasoning will ratify
it and the check will read as verification while providing none.

**5. Repair.** When a unit fails, diagnose the failure signature before reaching
for a bigger model. `references/escalation.md` maps signatures to the cheapest
repair. Most failures are contract bugs — missing context, absent bound, weak
check — and a tier bump fixes them at ten times the necessary price while leaving
the actual defect in place, where it will reappear on the next unit.

**6. Synthesize.** Assemble verified artifacts. This is genuinely top-tier work:
noticing that two agents' outputs contradict each other is exactly the
cross-cutting consistency check that lower tiers cannot do.

## Rules that pay for themselves

**Never retry unchanged.** A retry with identical input is a coin flip on
sampling. Every retry must carry something new — the error text at minimum, the
diagnosis ideally. If you cannot say what changed, escalate or re-brief instead.

**Escalate the contract before the model.** In order of cost: add the missing
context, tighten the bounds, narrow the unit, raise the budget, raise the tier.
Only the last one is expensive, and it is the last one for a reason.

**Verification must be cheaper than the work.** If checking an output costs as
much as producing it at a higher tier, the check is the bottleneck — route the
work up and delete the check. This is the honest limit of the whole approach.

**Keep the orchestrator out of the work.** If you find yourself writing
implementation code, the decomposition failed. Go back and split the unit. The
orchestrator's tokens are the most expensive in the system and its context is the
scarcest; spending them on boilerplate is the most common way this pattern
degrades into an expensive single-agent run.

**Cap the ladder.** A unit that has been escalated twice and still fails is not a
routing problem. Stop, surface what was tried and what the failure looks like,
and ask. Silent third escalations are how a cost-control framework produces the
largest bill of the week.

## Tools in this package

`bin/orchestrate` keeps the budget ledger. It records each dispatch and each
return, then reports spend against plan, escalations per unit, and any unit at
the escalation cap. It reports what happened; the routing calls stay yours.

```sh
bin/orchestrate record --unit u3 --event dispatch --tier 1 --tokens 12000
bin/orchestrate record --unit u3 --event escalate --note "missing fixture path"
bin/orchestrate report
```

Role prompts for the agents this loop dispatches are in `agents/`.

## Reference

- `references/routing.md` — the tier and budget scorecards, with worked examples
- `references/delegation-contract.md` — brief template and why each field exists
- `references/escalation.md` — failure signature to cheapest repair
- `references/economics.md` — handoff tax, split-vs-merge break-even, budget ledger
- `references/execution.md` — dispatch mechanics and parallelism patterns
- `references/roster.example.yaml` — model roster format

A companion `tier-plan` skill produces the plan this loop executes, and a
`model-fitness` skill fills the roster. Neither is required: this package works
alone, and the plan step below runs inline when no separate planner is present.
