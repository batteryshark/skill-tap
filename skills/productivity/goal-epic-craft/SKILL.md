---
name: goal-epic-craft
description: "Turn rough intent into a bounded goal or epic through a short interview, grade an existing goal against a written standard, or split a bounded epic into vertical slices. Use when a brief is too vague to execute, when asked to shape, bound, or scope a goal, epic, or project brief, or before delegating work to an autonomous agent."
---

# Goal and Epic Craft

Three workflows over one rubric, [references/STANDARD.md](references/STANDARD.md):
**craft** (rough intent in, bounded goal out), **grade** (score an existing
goal), **split** (bounded epic into vertical slices). Read the standard
first; it defines every term below. All three take and produce plain
markdown. Filing into a specific tracker is an optional integration —
[references/work-integration.md](references/work-integration.md).

## Craft

1. Take the user's words as given. Keep the original phrasing; it becomes
   the heart of `## Description`. No metadata questions yet.
2. Recon: facts are your job. Skim whatever the intent names — files, repos,
   trackers — and check for neighboring or overlapping work; use
   [agents/recon.md](agents/recon.md) for anything slow. The user answers
   decisions; the environment answers facts.
3. Interview in frontier rounds. Each round, ask every question from the
   standard's ready test whose prerequisites are settled: numbered, with
   your recommended answer, at most 5 per round; a typical session finishes
   in 2. The user may leave any decision to the executor — record it in
   `## Notes`; that counts as answered. Stop when the ready test drains.
4. Draft the full document to the standard; title short, meaning
   front-loaded. Show it, take one confirm round, and hand it over. Run
   `bin/goal-epic-craft DRAFT.md` and repair what it reports before showing.

## Grade

1. Load the document (pasted, file, or tracker item). Missing input: ask —
   never guess which item is meant.
2. Run `bin/goal-epic-craft FILE` for the mechanical evidence, then judge
   the rest in the standard's order: four properties, ready test, failure
   modes, fewer-sharper caps, epic check. [agents/grader.md](agents/grader.md)
   runs this as an independent pass.
3. Report: verdict first (**ready to hand off** or **blocked — N gaps**),
   then at most 5 gaps ranked by how badly each would misdirect an executor
   — failure-mode name, location, and the question whose answer cures it.
   Praise nothing; change nothing yourself.

## Split

1. Gate: run the grade workflow silently on the epic. Blocked input stops
   here — report the gaps and offer the craft workflow. Splitting an
   unbounded epic multiplies its gaps into every child.
2. Propose 3–7 children per the standard's epic extras: vertical, the first
   the walking skeleton; title plus one goal sentence ending in a pointer to
   the parent's purpose; 1–3 acceptance criteria each with a verification
   method; an ordering between siblings only when one truly cannot start
   first — a dependency chain is a horizontal split wearing a costume.
3. One confirm round. The deliverable is one block per child under the
   parent's title.

Whatever the workflow: the human promotes, schedules, or delegates the
result; never do that on their behalf.
