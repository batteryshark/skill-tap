---
name: decision-records
description: Create, recover, review, or update durable decision records that preserve context, constraints, considered alternatives, chosen direction, consequences, evidence, uncertainty, and reconsideration criteria. Use for architecture decisions, product or operational tradeoffs, design-rationale interviews, superseding stale records, or reconciling documented intent with actual practice.
---

# Decision records

Preserve why a consequential choice was reasonable under its constraints. Record the decision without turning inference into historical fact or presenting one option as universally correct.

## Choose a mode

- **Create:** document a decision being made now.
- **Recover:** reconstruct rationale from implementation, history, notes, and informed people.
- **Reconcile:** compare a record with current behavior and update, supersede, or flag drift.

## Workflow

1. Identify the decision boundary, affected people or systems, and the durable artifact location. Use an established local convention when one exists.
2. Gather direct evidence: requirements, implementation, tests, incidents, measurements, prior records, notes, and explicit maintainer statements.
3. Scaffold a record when useful:

   ```sh
   bin/decision-records --title "Choose the job queue" --output docs/decisions/job-queue.md
   ```

4. Capture context and binding constraints before the choice. Describe serious alternatives fairly, including why they were rejected under those constraints.
5. State the selected direction, expected benefits, accepted costs, risks, follow-up work, and observable validation.
6. Separate observed facts, quoted rationale, and inference. Use [`references/interview-and-reconciliation.md`](references/interview-and-reconciliation.md) when author context is missing or the record may be stale.
7. Define concrete reconsideration triggers. Mark a superseded or deprecated record in place and link its successor; do not silently rewrite historical context.
8. Review the result against [`references/record-schema.md`](references/record-schema.md).

## Rules

- Record consequential choices, not every implementation detail or preference.
- Keep current project status in the project's tracker or task system; keep durable rationale here.
- Preserve disagreement and uncertainty when they materially affect future change.
- Do not manufacture alternatives merely to make the record look complete.
- Describe consequences as tradeoffs, not promises.
- Never expose credentials, private personal context, or confidential values in a broadly shared record.

## Output

Return the record path or draft, status, evidence basis, confidence limits, confirmation questions, and any follow-up or reconsideration trigger.

Use [`agents/interviewer.md`](agents/interviewer.md) to recover context and [`agents/auditor.md`](agents/auditor.md) to challenge a draft or detect drift.
