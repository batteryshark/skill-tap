---
name: project-tracker
description: Create or update compact durable Markdown memory for long-running projects, including current objective, status, workstreams, attempts, decisions, important artifacts, open questions, and next actions. Use when capturing project state, reconstructing context, preparing a handoff, recording a pivot, or making future sessions resumable across engineering, research, automation, writing, and other multi-session work.
---

# Project tracker

Preserve the smallest durable project memory that lets a future collaborator resume accurately. This is a project artifact, not a transcript or a second task manager.

## Default shape

Use one dashboard at `.project/tracker.md`. Add `.project/sessions/` only when a session contains detailed evidence that would overload the dashboard. Follow [`references/tracker-schema.md`](references/tracker-schema.md) unless the project already has a clear local convention.

Scaffold or inspect the tracker with:

```sh
bin/project-tracker init PROJECT --title "Project name"
bin/project-tracker session PROJECT --title "Short session title"
bin/project-tracker status PROJECT
```

## Workflow

1. Read any existing tracker before updating it.
2. Extract durable facts from the current conversation and project evidence: objective, pivots, attempts, results, artifacts, decisions, questions, and next actions.
3. Inspect the project enough to ground claims in files, commands, logs, or outputs. Mark unknown history rather than reconstructing it from guesswork.
4. Update `.project/tracker.md` so current state, ownership, blockers, and the evidence that would close each active workstream are visible without reading old sessions.
5. Add a timestamped session note only when raw evidence, failed approaches, or detailed results will materially help future work.
6. Move resolved questions and completed work to concise history; do not let the active dashboard grow indefinitely.
7. Route side thoughts with [`references/capture-routing.md`](references/capture-routing.md) instead of copying every thought into the tracker.

## Rules

- Use relative project paths unless an absolute path is itself the environment issue.
- Separate observed facts, decisions, theories, and unknowns.
- Never store credentials, tokens, cookies, private keys, or unrelated personal data.
- Preserve useful failed approaches and reconsideration triggers, but compress raw process history.
- Keep a concise decision summary in the tracker when it changes project direction. Put durable rationale that should outlive the active project state in the project's decision-record convention and link it from the tracker.
- Keep actionable backlog in the project's established issue or task system when one exists.
- Do not create many ledger files by default; split only when the dashboard has a proven maintenance problem.

## Report

State which tracker files changed, the new current objective and next action, and any history that could not be verified.

Use [`agents/recorder.md`](agents/recorder.md) for an evidence-grounded tracker update.
