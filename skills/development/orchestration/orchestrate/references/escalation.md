# Escalation: diagnose before you upgrade

A unit came back wrong. The reflex is to send it up a tier. The reflex is usually
expensive and usually wrong.

Most delegated failures are not capability failures. They are missing context,
absent bounds, weak checks, or units that were too large — and a bigger model
papers over all four. The work gets done, the bill goes up ten times, and the
actual defect stays in the contract where it will reproduce on every remaining
unit of the same shape. That last part is what makes reflexive escalation costly
in aggregate rather than merely wasteful once.

So: read the failure signature first. It tells you which repair is the cheap one.

## Signature to repair

| What came back | What it means | Cheapest repair |
|---|---|---|
| Same error class each attempt, converging | Mechanical, in progress | Retry same cell; raise retry limit if it is trending |
| Different error each attempt, thrashing | Wrong approach, no model of the problem | +1 budget first; +1 tier only if that fails |
| Asked clarifying questions, or stalled | Contract underspecified | Fix the contract, redispatch same cell |
| Well-formed output, confidently wrong | Missing context, not missing capability | Add the specific context, same cell |
| Passed the check but the result is bad | The check is weak | Strengthen VERIFY, redispatch same cell |
| Huge diff, unrequested extras | No out-of-scope list | Add bounds, redispatch same cell |
| Ran long, plausible, unverifiable | Unit too large to check | Decompose into checkable pieces, same cell |
| Refused to commit, returned options | Objective asked to explore | Reword to demand a decision, same cell |
| Claimed success, artifact absent or wrong | Honesty failure | Do not retry — this model is not delegatable. See below |
| Correct, careful, and still not good enough | Genuine capability ceiling | +1 tier, +1 budget |

Only the last row is a real tier bump. Track how often you land there. If it is
most of your escalations, your tier scores are running low and the rubric in
`routing.md` is being applied optimistically. If it is almost none, you are
routing too high and leaving money on the table.

## The ladder, cheapest first

1. **Add the missing context.** Often one file, one prior decision, one example
   of the expected shape. Costs a few thousand input tokens.
2. **Tighten the bounds.** Out-of-scope list, output format, an escape hatch.
   Costs a few hundred tokens.
3. **Narrow the unit.** Split it so each piece has its own check. Costs one extra
   handoff and usually converts an unverifiable unit into two verified ones.
4. **Raise the budget.** Same model, more search. Costs output tokens at the same
   rate — the cheapest real capability increase available.
5. **Raise the tier.** Costs the rate difference on everything the unit consumes,
   plus a full context reload.

Steps 1–3 are contract repairs, and they generalize: fixing the contract fixes
every remaining unit built from the same template. Steps 4–5 are capability
purchases and they apply to one unit only. Prefer the repairs, and when you do
make a purchase, ask whether the contract template needs the same fix anyway.

**Every rung carries the evidence forward.** The next attempt gets the failed
attempts, the error output, and the partial artifacts — not a fresh copy of the
original task. Failed attempts are expensive information about where the problem
actually is; discarding them means paying to rediscover it. This is also what
keeps a re-dispatch from being a retry-unchanged in disguise, since the evidence
is the thing that changed.

## Honesty failures are terminal

A model that reports success without producing the artifact cannot be used in a
self-verifying loop, at any tier, at any price. The entire escalation model rests
on failure reports being true — that is the signal the whole loop runs on. Once
it is unreliable, every "pass" needs independent checking, and independent
checking of everything costs more than doing the work at a higher tier.

If you see this, stop delegating to that model in loops. Either use it only for
transforms whose output the orchestrator reads directly, or drop it from the
roster. `model-fitness` gates on this before it gates on anything else, and it is
the one probe with no partial credit.

## Budget-raise before tier-raise

Worth stating separately because it is the step most often skipped.

Raising the reasoning budget on the same model is the cheapest genuine increase
in capability available. It costs output tokens at the rate you are already
paying, needs no context reload, and frequently closes gaps that look like tier
gaps — thrashing, shallow analysis, missed constraints, and premature commitment
are all search failures, not knowledge failures.

The diagnostic that separates the two dials: **budget fixes "didn't think it
through"; tier fixes "couldn't have known."** If the return shows the model had
everything it needed and drew the wrong conclusion, buy reasoning. If it shows
missing knowledge, misread intent, or a capability that simply is not there, no
quantity of thinking tokens will supply it — escalate the tier. Two budget raises
that both fail is the same verdict arriving more slowly, so stop after the
second.

The reverse is also true and also worth checking: if a unit succeeded on the
first attempt at deep budget, try the next one at moderate. The plateau is often
lower than assumed, and `model-fitness` measures exactly where it sits.

## Stop conditions

Escalation is a loop and loops need exits.

- **Two escalations, still failing.** Stop. Report what was tried, what each
  attempt returned, and what you believe the blocker is. A third escalation on a
  unit that has already resisted two is more likely a misunderstood problem than
  an under-powered one.
- **Escalation cost exceeds doing it top-tier from scratch.** You have already
  lost the bet. Discard the partial work, run it at T3 clean, and note the unit
  shape so the next plan routes it correctly the first time.
- **The same signature on three units in a row.** That is a template defect. Stop
  dispatching, fix the contract template, then resume. Repairing after the fact
  on a batch of forty is how a cost-saving run becomes the expensive one.
