# Filter Rubric

Use this rubric to decide what belongs in the deliverable.

## Classifications

| Classification | Meaning | Action |
|---|---|---|
| Keep | Human-facing source, config, docs, or tests that reduce maintenance cost. | Leave it or improve it in place. |
| Delete | Dead code, redundant tests, obsolete docs, old plans, unused shims, or process residue. | Remove it after confirming it is not load-bearing. |
| Distill | Raw context contains useful rationale, but the artifact is not useful as-is. | Move the durable idea into names, code structure, comments, ADRs, or concise docs. |
| Move to scratch | Useful only during the current agent run. | Put it under `.agent-work/deliverable-hygiene/<run-id>/`. |
| Block | Important but unsafe to decide from evidence. | Stop and ask, or leave a blocked run folder with the evidence. |

## Violation Categories

Agent residue:

- Temporary reports, prompts, plans, scratch diffs, model outputs, review dumps, and loop state in the project surface.
- Tool-specific work folders, chat histories, prompt dumps, and temporary worktrees committed into the repo.
- Markdown files whose only audience is the agent that created them.

Documentation sprawl:

- Multiple overlapping READMEs or architecture notes.
- Status reports, implementation notes, or handoff docs that repeat source control.
- Docs that explain old behavior after the code moved on.

Test theater:

- Tests that assert private helper structure instead of behavior.
- Mock-heavy tests that only verify a mock was called.
- Large snapshot files that hide intent.
- Redundant edge-case grids with no real risk difference.
- Skipped tests with no concrete reason or removal condition.

Monolithic mental-load hotspots:

- Files or functions that force the reader to track unrelated concerns at once.
- Mixed parsing, validation, policy, IO, and presentation in one flow.
- Abstractions whose names do not reveal ownership or purpose.

Weak comments:

- Comments that narrate syntax.
- Stale or speculative comments.
- TODOs with no owner, reason, or completion condition.
- Agent-process commentary.

Generic AI code shape:

- Names such as `manager`, `processor`, `handler`, `helper`, `data`, `result`, or `utils` when the domain has better vocabulary.
- Defensive branches with no defined failure contract.
- Broad fallback behavior that hides errors.
- Duplicated helpers created for adjacent cases without a real shared concept.

Legacy fossils:

- Compatibility shims without current callers.
- Old migrations, flags, adapters, and alternate code paths kept only because they used to matter.
- Dead public API aliases when the project is allowed to break.

## Evidence Standard

Every finding needs evidence:

- File path and line or narrow file region when possible.
- Why the artifact increases cognitive load or violates the doctrine.
- Recommended action: keep, delete, distill, move, or block.

Do not fail code because it "feels AI-generated." Fail it because a human-maintenance cost is visible in the repository.
