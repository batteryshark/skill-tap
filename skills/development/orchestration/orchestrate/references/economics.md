# Economics: when the split actually pays

Every routing decision is a bet with a known price and an estimated win rate.
This file gives the arithmetic. It is simple arithmetic and the point of writing
it down is not precision — the inputs are estimates — but direction. It reliably
tells you which side of a line you are on, and the lines are further from
intuition than they look.

## The handoff tax

A handoff costs more than the message. Per hop, roughly:

- **Brief tokens** — the contract, plus every artifact the receiver must read to
  act on it. This is usually the dominant term and it is easy to underestimate,
  because "just read these three files" is ten thousand tokens.
- **Return tokens** — the reply, plus whatever the orchestrator reads to verify
  it, at orchestrator rates.
- **Latency** — a full round trip, which matters on the critical path and not at
  all off it.
- **Information loss** — the receiver does not have the conversation. It will
  make locally reasonable choices that are globally wrong, at some rate.

Only the first two are billable, and together they are what `handoff_tax` in the
roster estimates. A few thousand tokens is typical. Measure it once for your
setup rather than guessing; it anchors every decision below.

## Split or merge

Splitting a unit off to a cheaper tier saves the rate difference on the work and
pays the tax at the higher rate.

```
split pays when:   work_tokens × (rate_high − rate_low) > handoff_tokens × rate_high
```

Divide through by `rate_high` and let `r = rate_low / rate_high`:

```
split pays when:   work_tokens × (1 − r) > handoff_tokens
```

With a 10× price gap (`r = 0.1`), that is `work_tokens > 1.1 × handoff_tokens` —
split whenever the work is larger than the brief. With a 3× gap (`r = 0.33`), it
is `work_tokens > 1.5 × handoff_tokens`.

**The practical rule: split when the delegated work is at least twice the size
of the brief needed to describe it. Otherwise merge upward.**

Twice, not 1.1×, because the arithmetic above ignores the failure path. A cheap
tier fails some of the time, and each failure costs the retry plus, eventually,
the escalation. Doubling the threshold absorbs that without needing a second
calculation.

### Merge, concretely

Merge when the execution is a single reliable tool call and the analysis is the
real work. Splitting "run the decompiler" from "read the decompiler output" means
shipping the C pseudocode across a handoff so the analyst can read what the
executor already had in context. You paid the tax to move data between two agents
when one agent could have held both ends.

**Trigger: one-shot retrieval or a guaranteed tool call feeding analysis.** Let
the analytical tier call the tool and evaluate the result in one context.

### Split, concretely

Split when execution requires iteration, brute force, or debugging. That is where
the token volume is, and it is volume with a check on it — exactly the shape a
cheap tier handles safely.

**Trigger: the work will generate tracebacks.** Let the cheap tier loop to green,
then hand the clean artifact — not the debugging transcript — up for analysis.

The asymmetry is the point. Debugging generates enormous token volume of near-
zero informational value. Every traceback the expensive model reads is money
spent on a line that will not appear in the final answer. Push that volume down
and hand up only the result.

### Where to put the seam

Pass artifacts, not transcripts. A file, a table, a diff, a clean log — something
compact that stands on its own.

That gives a clean test for whether a split point is right: **if the receiving
side needs the sending side's full context to act, the seam is in the wrong
place.** Move it to wherever a compact artifact crosses the boundary. A handoff
that requires shipping the whole upstream conversation is not a handoff, it is
context duplication with a tax on it — you pay to move the context and then pay
again to have it read.

## Escalation break-even

Starting low is a bet. It pays when:

```
c_low + p_fail × (c_low × retries + tax + c_high)  <  c_high
```

Solving for the win rate you need, with `r = c_low / c_high` and `t = tax / c_high`:

```
p_success  >  (r + t) / (1 + t)         [approximately, for small retry counts]
```

With `r = 0.1` and a tax around 20% of the high-tier cost, that is roughly
`p_success > 0.25`. With a 3× gap and a heavier tax it climbs past 0.5.

**The rule of thumb: if you would bet even money that the cheap tier lands it,
route down. If you would not, start high.** Below a coin flip, the escalation
path dominates and you are paying twice for one result.

Two things move the odds enough to change the answer:

- **Strong verification raises effective `p_success`** — not because the model is
  better but because failures are caught cheaply and retried instead of
  escalating. This is why `verification` subtracts in the tier scorecard.
- **A large unit raises the stakes on both sides** — more savings when it works,
  more waste when it does not. Large uncertain units are the worst bet on the
  board. Split them until each piece is either confidently cheap or clearly not.

## Verification must be cheaper than the work

If checking an output costs as much as producing it one tier up, the check is the
bottleneck. Route the work up and delete the check.

This is the honest limit of the approach. Delegation downward is only free when
verification is nearly free. When it is not — when correctness is a matter of
expert reading — the tier structure stops helping and you are choosing between
paying for capability and accepting risk. Say that plainly rather than
manufacturing a check that does not check anything, which converts an obvious
cost into a hidden one.

## The budget ledger

Track spend as you go, at whatever granularity your dispatch mechanism reports.
The ledger exists so that running out of budget is a decision rather than a
surprise.

Per unit: cell dispatched to, attempts, tokens, outcome, and — the one worth
recording — whether the cheap route actually paid. A tally of "routed down,
escalated anyway" is the calibration signal for everything above. If it runs high
on a particular unit shape, that shape's tier score is systematically low.

Degrade in this order when budget tightens:

1. **Drop budget levels before dropping tiers.** Cheaper and it hurts less.
2. **Cut redundancy before cutting coverage.** Three verifiers on one finding
   goes before checking a whole class of findings at all.
3. **Cut breadth, and say what you cut.** A truncated sweep reported as complete
   is worse than an honest partial one, because the reader acts on it as if it
   were complete. Name what was skipped.
4. **Never cut verification on anything with blast radius 2.** That is the
   spend that was buying the most.
