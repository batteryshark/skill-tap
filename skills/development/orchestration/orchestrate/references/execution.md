# Execution: how to actually dispatch

The routing decision is abstract. This is where it meets a tool call.

## Choosing a dispatch mechanism

**Subagents (the `Agent` tool)** — the default. Launch every unit with no unmet
dependency in a single message so they run concurrently. Continue an existing
agent with `SendMessage` when the follow-up needs its context; start a fresh
`Agent` when it does not, since inheriting a polluted context costs more than
re-briefing.

**A workflow engine** — deterministic multi-stage fan-out with structured
returns, per-agent model and effort control, and pipelines that let item A reach
stage 3 while item B is still in stage 1. Better for large repeated shapes.

The constraint that matters: **the `Workflow` tool requires explicit user opt-in.**
It can spawn many agents and spend heavily, so it is only available when the user
asked for it in their own words, turned it on for the session, or invoked a skill
that calls it. Do not reach for it because a job looks like it would suit one. If
a job would clearly benefit, do the scouting inline, then say what a workflow
would do and roughly what it would cost, and let them decide.

**External models** — anything with a CLI or an API. The roster's `invoke` field
says how. Dispatch through `Bash`, write the artifact to a file, read the file
back. Keep returns on disk rather than in stdout when they are large; a big
stdout capture lands in the orchestrator's context, which is the context you are
trying to protect.

**Inline** — below the floor in `SKILL.md`. Just do it.

## Setting the two dials

**Tier → model.** Pick the cheapest roster entry whose `tier_ceiling` meets the
required tier. With subagents that is the `model` parameter; with external
models it is whatever `invoke` specifies.

**Budget → reasoning effort.** How this is set depends on the mechanism:

- A workflow engine typically exposes an explicit effort parameter per agent.
  Use it — it is the direct control.
- The plain `Agent` tool has no effort parameter. Budget is set through the
  prompt and it works: say *"this is mechanical, do not overthink it — run the
  command, read the output, fix, repeat"* for minimal, and *"think carefully
  about the failure mode before proposing anything; consider at least three
  explanations and say why you rejected the ones you rejected"* for deep.
- External models vary. Some take a reasoning parameter, some respond to prompt
  framing, some have neither. Record which in the roster's `budgets` field so
  the planner does not route a deep unit to a model that cannot go deep.

Prompt-level budget control is weaker than a parameter, so be explicit about it
in the contract rather than assuming the default lands where you want. The
default is usually moderate, which means minimal units are quietly overpaying and
deep units are quietly under-thinking.

## Parallelism

**Fan out on independence, not on convenience.** Two units are independent when
neither reads the other's output *and* they do not write the same files. The
second half is the one that bites: concurrent agents editing the same file
produce a mess no one can untangle. Either partition by file, serialize them, or
give each an isolated worktree if your mechanism supports it. Isolation is not
free — prefer partitioning when you can.

**Prefer pipelines to barriers.** A barrier makes every unit wait for the
slowest. Let each item flow through its stages as soon as its previous stage
finishes. Barriers earn their cost only when the next stage genuinely needs all
prior results at once — deduplication across the full set, an early exit on a
zero count, or a comparison that references the other findings.

**Cap concurrency on shared resources.** Rate limits, a build lock, a single test
database. Ten agents contending for one resource are slower than three and
generate spurious failures that look like capability problems.

## Getting structured returns

If your mechanism can enforce an output schema, use it. Validation at the tool
layer means malformed returns are retried by the machinery instead of reasoned
about by the orchestrator, and it removes an entire class of parsing work from
the most expensive context in the system.

Without schema enforcement, ask for a small fixed set of named fields plus
artifact paths, and keep prose out of the return. Prose returns are how
orchestrator context fills up with narrative about work instead of the work.

## Verifying returns

Read artifacts, not reports. Concretely, for each returned unit:

1. Run the VERIFY command yourself — or confirm the returned output is the real
   thing rather than a description of it.
2. Confirm the artifact exists and has plausible size and shape.
3. Spot-check one item per batch against the source. Batch classification is the
   easiest place for confident drift to hide, because every row looks fine.

This costs a little and catches the failure that is worst to inherit: work that
is wrong in a way synthesis will not notice.

## Two patterns worth having ready

**Sweep.** Many similar units, one shape. Write one contract template, dispatch
in batches sized to your concurrency cap, verify each return, and watch for a
repeated failure signature — three in a row means fix the template before
continuing rather than repairing forty results afterward.

**Funnel.** Cheap broad pass narrows to expensive deep pass. Bulk extraction or
classification at low tier over everything, then the top tier over only what
survived. The saving is the ratio of input volume to survivor volume, so the
funnel is worth building when that ratio is large and worth skipping when it is
not. A funnel over thirty items is overhead; over three thousand it is the
difference between feasible and not.
