# Doctrine

## Finished Work, Not Workbench

The repository is the artifact a human inherits. It should contain the smallest useful set of source files, configuration, durable docs, and behavior tests. It should not contain the agent's scaffolding, temporary reasoning, iteration reports, or defensive clutter.

Agents may need large amounts of context to do good work. That context belongs in scratch space while the work is in progress. Only distilled human value survives into the project.

## Human Mental Bandwidth

Optimize for a maintainer reading under pressure:

- Make the main path obvious.
- Keep related ideas close together.
- Prefer names and structure that explain themselves.
- Avoid abstractions that exist only because the agent found a pattern.
- Avoid clever tricks unless the code or a short nearby comment makes the trick legible.

Complex systems are allowed. Confusing systems are not. If the system cannot be explained simply, keep refining its shape.

## Hard Change Default

For greenfield work and explicit cleanup, prefer complete replacement over compatibility fossils:

- Remove old code paths when the new path replaces them.
- Delete unused feature flags, fallback branches, migration helpers, and wrappers.
- Do not keep "just in case" shims.
- Do not preserve original behavior unless the user, public API, persisted data, or explicit project evidence requires it.
- If compatibility touches a public API, persisted data, or possible external callers and breakage permission is not explicit, block for confirmation.

Understand before deleting, then delete completely. Half-preserved legacy code is usually worse than a clean break.

## Code-First Rationale

Put rationale in the smallest durable place that helps a human:

- First, improve names and structure.
- Then add concise local comments for non-obvious intent, constraints, hazards, or external quirks.
- Use ADRs or architecture docs for decisions that cross modules or cannot be understood locally.
- Use `.project/` only when durable project memory helps humans steer long-running work.

Do not commit raw session summaries, planning transcripts, agent reports, or "what I did" notes as project docs.

## Behavioral Minimum Tests

Tests earn their place by protecting or explaining behavior:

- Keep tests for public contracts, risky transformations, domain rules, bug regressions, and important failure modes.
- Delete or rewrite tests that only mirror private implementation, assert incidental mocks, duplicate coverage, or make refactoring harder without protecting behavior.
- If a poorly shaped test is the only coverage for important behavior, rewrite it as a behavior test before deleting the original.
- Prefer a few clear tests over broad test theater.

## Useful Comments

Comments should preserve human context the code cannot carry:

- Why an unusual branch exists.
- What external contract forces a shape.
- What hazard a future maintainer must not break.
- What algorithmic or domain tradeoff matters.

Delete comments that narrate syntax, repeat names, preserve obsolete history, excuse bad structure, or describe the agent's process.

Keep TODO comments only when they include the reason, owner or trigger, and completion condition. Otherwise delete them or convert the work into the project's normal tracker.
