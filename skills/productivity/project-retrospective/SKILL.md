---
name: project-retrospective
description: Turn a completed or paused body of work into an evidence-based retrospective covering goals, outcomes, decisions, pivots, effective practices, friction, failed approaches, unfinished work, open questions, and concrete improvements. Use with conversation history, project trackers, session notes, plans, logs, or user-specified files and folders across engineering, research, writing, automation, and other projects.
---

# Project retrospective

Extract lessons from what happened without turning the result into blame, self-congratulation, or a transcript.

## Inputs

Use the current conversation and any sources the user explicitly places in scope. For files or folders, run `bin/project-retrospective SOURCE...` to inventory supported text and `--emit` only when the collected content is appropriate to place in the current context.

Do not search private session stores, chat databases, home directories, or unrelated project history unless the user explicitly names them.

## Workflow

1. Define the work period, audience, and sources. State any important missing evidence.
2. Gather goal statements, plans, tracker state, changed artifacts, validation output, corrections, decisions, failed attempts, and unfinished work.
3. Build a factual timeline before interpreting success or friction.
4. Analyze with [`references/analysis-rubric.md`](references/analysis-rubric.md). Separate outcome quality from process quality.
5. Draft with [`references/retro-template.md`](references/retro-template.md). Omit inapplicable sections instead of writing filler.
6. Tie each lesson to evidence and a repeatable action. Keep proposed skills or safeguards specific enough to implement.
7. Present the retrospective in the requested location. Do not create a permanent retro file unless the user asked for one.

## Rules

- Distinguish original goals from later pivots.
- Credit smooth work and successful corrections alongside failures.
- Describe mistakes and communication friction neutrally, with the information available at the time.
- Do not invent message counts, timing, files changed, or causal explanations.
- Quote only short excerpts that materially establish a lesson.
- Exclude credentials, tokens, cookies, private keys, and unrelated personal data.
- Prefer two or three high-value improvements over a long generic suggestion list.

## Output

Produce a self-contained retrospective with sources, confidence limits, concrete evidence, and prioritized follow-up actions.

Use [`agents/analyst.md`](agents/analyst.md) for an independent retrospective pass.
