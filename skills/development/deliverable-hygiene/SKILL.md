---
name: deliverable-hygiene
description: Keep or restore a codebase as a finished, human-readable work product by separating agent scratch from source, pruning excess documentation and tests, deleting obsolete compatibility paths, and validating that process residue does not leak into the deliverable. Use during implementation cleanup or when a repository has visibly drifted.
---

# Deliverable hygiene

Keep the repository shaped like the artifact a human maintainer should inherit. Optimize for a clear mental model, a small useful surface, behavior-focused tests, and complete removal of obsolete paths.

## Choose a mode

Use **doctrine mode** while adding or changing code:

1. Read enough of the repository to understand its current model.
2. Keep temporary reasoning and agent state outside the deliverable.
3. Apply the rules in [`references/doctrine.md`](references/doctrine.md) while editing.
4. Validate that the final repository is easier to understand than the starting point.

Use **recovery loop mode** when the repository has accumulated residue:

1. Run `bin/deliverable-hygiene <repo>` to collect review candidates.
2. Audit concrete violations using [`references/filter-rubric.md`](references/filter-rubric.md).
3. Fix high-confidence findings without widening the requested scope.
4. Validate from repository evidence.
5. Repeat for at most three passes, then stop `GREEN`, `BLOCKED`, or `CAPPED`.

Read [`references/workflow.md`](references/workflow.md) before recovery loop mode. Use [`references/examples.md`](references/examples.md) when a classification is unclear.

## Core rules

- Treat the repository as the deliverable. Keep plans, prompts, review dumps, and loop state in disposable scratch space.
- Put recovery state under `.agent-work/deliverable-hygiene/<run-id>/` and ensure `.agent-work/` is ignored.
- Prefer names, structure, and concise local comments over new documents.
- Preserve compatibility only when a public contract, persisted data, explicit requirement, or repository evidence makes it real.
- Keep tests that protect meaningful behavior. Rewrite or remove tests that freeze private structure.
- Add comments for intent, constraints, hazards, and external quirks that code cannot express.

## Delegation

The portable role prompts in `agents/` separate evidence gathering, editing, and validation:

- [`agents/auditor.md`](agents/auditor.md)
- [`agents/fixer.md`](agents/fixer.md)
- [`agents/validator.md`](agents/validator.md)

Run the roles sequentially when independent subagents are unavailable. The fixer must verify the auditor's evidence, and the validator must inspect the repository rather than trust the fixer's summary.

## Report

State the mode, categories fixed, files changed, checks run, final verdict, and any decision still blocked. Delete successful scratch before reporting.
