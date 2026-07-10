---
name: code-quality-review
description: Review or improve source code for reader-facing maintainability across naming, functions, models, comments, error handling, tests, external boundaries, and concurrency. Use for broad code-quality audits, behavior-preserving cleanup, generated-code humanization, refactoring prioritization, or focused requests to reduce local cognitive load without redesigning the whole architecture.
---

# Code-quality review

Improve code from repository evidence rather than a universal style checklist. Optimize for accurate intent, safe change, and the conventions of the language and project under review.

## Choose a mode

Use **audit mode** when asked to review, diagnose, or prioritize. Report findings without editing.

Use **cleanup mode** when asked to improve or refactor. Make small, behavior-preserving changes and validate each coherent step.

## Workflow

1. Read manifests, source layout, formatter and linter configuration, tests, and representative execution paths.
2. Run `bin/code-quality-review <repo>` for a neutral inventory of languages, large files, tests, and debt markers. It follows Git ignore rules by default; use `--include-ignored` only when ignored source is explicitly in scope.
3. Classify concrete issues with [`references/review-rubric.md`](references/review-rubric.md). Ignore generated, vendored, dependency, build, and minified code unless it is explicitly in scope.
4. When needless machinery is the concern, use [`references/complexity-pruning.md`](references/complexity-pruning.md) to look for deletion and consolidation opportunities without assuming every abstraction is waste.
5. Prioritize correctness hazards, hidden failure behavior, missing behavioral coverage, and high-cost comprehension problems before cosmetic consistency.
6. In cleanup mode, follow [`references/safe-refactoring.md`](references/safe-refactoring.md). Preserve public APIs, serialized shapes, persisted data, and externally observable behavior unless migration is explicit.
7. Apply the repository's language conventions. Read [`references/language-guidance.md`](references/language-guidance.md) only for the languages present.
8. Run the narrowest relevant tests, type checks, linters, formatters, or build commands.

## Rules

- Treat metrics and patterns as investigation leads, not verdicts.
- Explain the reader or behavior cost of every finding.
- Prefer domain vocabulary over generic names, but do not rename public contracts casually.
- Split functions, classes, or modules by coherent responsibility rather than line-count thresholds.
- Remove duplication only when the shared concept is real.
- Keep comments for intent, constraints, hazards, and external quirks; improve code when a comment would only narrate it.
- Prefer deleting dead flexibility, using an existing platform capability, or consolidating a pass-through layer before introducing another abstraction.
- Prefer tests of observable behavior over tests that freeze private structure.
- Do not infer poor quality or authorship merely because code looks generated.

## Report

For audits, order findings by risk and include evidence, impact, action, and confidence. For edits, summarize reader-facing improvements, protected behavior, checks run, and residual risk.

Use [`agents/auditor.md`](agents/auditor.md) for an independent review, [`agents/simplifier.md`](agents/simplifier.md) for a deletion-focused pass, and [`agents/fixer.md`](agents/fixer.md) for a bounded cleanup pass.
