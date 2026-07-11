---
name: tetromino-guideline-review
description: Audit or plan a single-player falling-tetromino implementation against an explicit historical gameplay baseline covering field geometry, seven-bag generation, controls, lock-down, scoring, spins, game-over, UI, and audio. Use for evidence-based implementation reviews or remediation plans; this is an unofficial engineering checklist, not Tetris certification.
---

# Tetromino Guideline Review

Audit observable behavior against the bundled baseline. Do not imply endorsement, licensing, or official certification.

## Workflow

1. Read [references/provenance-and-scope.md](references/provenance-and-scope.md).
2. Read [references/core-rules.md](references/core-rules.md) and [references/ui-rules.md](references/ui-rules.md).
3. Locate engine, input, scoring, state, UI, option, and audio code.
4. Record each rubric rule as `PASS`, `FAIL`, or `UNKNOWN` with concrete file, test, or runtime evidence.
5. Save statuses as JSON and run `bin/tetromino-guideline-review score <file>`.
6. Render findings with [references/report-template.md](references/report-template.md).

Prefer `UNKNOWN` to inference. Under `code-only`, do not claim timing or audiovisual behavior that source inspection cannot establish.

