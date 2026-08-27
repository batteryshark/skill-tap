# The delegation contract

Most delegation failures are contract failures. The executor did exactly what it
was told; what it was told was ambiguous, unbounded, or uncheckable. This is
easy to misdiagnose as a capability problem because the symptom — wrong output —
looks identical, and the fix that appears to work (a bigger model) is the one
that masks the defect rather than removing it.

The contract exists to make the executor's job decidable: it should be able to
tell, without asking you, whether it is finished and whether it is right.

## Template

```
OBJECTIVE
  One sentence. The end state, not the steps.

INPUTS
  Exact paths, offsets, identifiers. Never "the config file" — which one.

PROCEDURE                      [omit for T2/T3; they choose their own]
  The steps, if the steps are known and you want these steps specifically.

VERIFY
  The exact command to run.
  What output or exit code means pass.
  What it looks like when it fails.

OUT OF SCOPE
  The specific things not to do. See below — this field does the most work.

RETRY
  Attempt the fix at most N times. On the Nth failure, stop and return the
  error output and what you tried. A halt with evidence is a success.

RETURN
  The exact shape of the reply. Paths of artifacts written, plus whatever
  structured fields the orchestrator will read.
```

## Why each field

**OBJECTIVE as end state, not steps.** Steps invite literal compliance with a
broken plan. An end state lets the executor notice that your steps were wrong,
which is most of the value of delegating to something that can think at all.

**INPUTS as exact references.** Ambiguous inputs are the most common cause of an
executor going off and reading half the repo to figure out what you meant. That
exploration is billed to you at the executor's rate and lands in its context
where it crowds out the actual work.

**PROCEDURE only when you mean it.** Specifying steps to a T2 or T3 executor
throws away the judgment you are paying for. Specify steps at T1, where judgment
is not on offer and improvisation is the failure mode.

**VERIFY as a runnable command, not an instruction.** "Make sure it works" is
not a check — it delegates the definition of "works" back to the executor, which
is the thing you were trying to pin down. A command with a stated pass condition
turns the unit self-verifying, which is what makes a low tier safe and lets the
retry loop run without you in it.

If you cannot write the verify command, that is real information: this unit
scores `verification = 0` and routes a tier higher. Do not paper over it with a
vague instruction.

**OUT OF SCOPE, the field people skip.** Capable models fill silence with
initiative. Left unbounded, they refactor adjacent code, add error handling you
did not ask for, upgrade dependencies, write a test framework. Every one of those
is defensible in isolation and collectively they are why a delegated unit returns
a 900-line diff for a 12-line change.

Name the specific temptations this unit presents, not generic prohibitions:

> Out of scope: do not modify the caller. Do not add logging. Do not fix the
> unrelated type error in the same file — it is tracked separately. If the fix
> seems to require touching `parser.py`, stop and report instead.

That last clause is the important one. An escape hatch converts scope violations
into halts, which are cheap, instead of into surprises, which are not.

**RETRY with a halt condition.** Unbounded retry burns budget silently. But the
number matters less than the framing: **halting with evidence is a successful
outcome**, not a failure. Say so explicitly. Executors that believe failure is
unacceptable will fabricate success, and a fabricated success is far more
expensive than an honest halt because it poisons everything downstream.

Set N by what a retry costs: 3–4 for a fast local check, 1–2 for a slow or
expensive one.

**RETURN shape.** The orchestrator has to read this. Free-form prose means the
orchestrator spends its expensive context parsing narrative. Ask for artifact
paths and a small number of named fields. If your dispatch mechanism supports
schema-enforced output, use it — validation at the tool layer means a malformed
return is retried by the machinery rather than reasoned about by you.

## Tier-specific emphasis

**T1** — the procedure and the verify command carry the weight. Give the exact
invocation. Give a known-good sample if one exists. Assume no intent will be
inferred correctly, because inferring intent is precisely what this tier does not
do; anything unstated will be filled with something plausible and wrong.

**T2** — the rubric and the out-of-scope list carry the weight. Supply a closed
list of categories, and always include an explicit "none of these / uncertain"
option. Without an escape bucket, every item gets forced into the nearest
category and your classification silently becomes noise. Constrain the output
format tightly; T2 drifts toward essays when it should be emitting a table.

**T3** — the objective and the constraints carry the weight. Say what must remain
true, what has already been decided and is not up for reconsideration, and what
the deliverable is. The failure mode here is not incapacity but scope: reopening
settled questions, or delivering an exploration when you needed a decision. If
you want a commitment, ask for a commitment and say that hedging is not an
acceptable return.

## Example: T1

```
OBJECTIVE
  scripts/dump_header.py exists and prints the 6 header fields for any ROM in
  samples/, matching the reference output exactly.

INPUTS
  Format notes:   docs/rom_header.md
  Test ROMs:      samples/*.rom
  Reference:      samples/expected/<romname>.txt

VERIFY
  python -m pytest tests/test_dump_header.py -q
  Pass: exit 0.
  Fail: pytest prints a diff of expected vs actual field values.

OUT OF SCOPE
  Do not modify anything under samples/ or tests/. Do not add a CLI framework —
  argparse or sys.argv is fine. Do not handle ROM formats beyond the six fields
  in the notes.

RETRY
  Up to 4 attempts. If tests still fail, stop and return the last pytest output
  plus a one-line note on which field you could not resolve. Halting with that
  evidence is the correct outcome — do not guess to make the test pass.

RETURN
  status: pass | halted
  artifact: scripts/dump_header.py
  if halted: failing_field, last_output
```

## Example: T2

```
OBJECTIVE
  Bucket each crash in crashes.jsonl by failure mode.

INPUTS
  crashes.jsonl — one crash per line, fields: id, stack, os, build

RUBRIC
  Exactly one of: oom | null-deref | race | disk-full | third-party |
  unknown. Use "unknown" freely — a wrong bucket costs more than an honest
  unknown, and the unknowns are what the next stage looks at first.

OUT OF SCOPE
  Do not propose fixes. Do not read the source tree. Do not merge or dedupe
  crashes. One row in, one row out.

RETURN
  CSV to triage.csv with columns: id, bucket, confidence(high|low), evidence
  (the single stack line that decided it).
```

The evidence column is doing quiet work: it makes a T2 classification spot-
checkable by the orchestrator at a glance, which converts an unverifiable unit
into a partially verified one and lets it stay at T2.
