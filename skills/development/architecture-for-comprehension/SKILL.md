---
name: architecture-for-comprehension
description: Evaluate a repository's architecture for coherence, discoverability, predictable execution paths, local reasoning, accidental complexity, and cognitive load. Use for system-level architecture reviews, onboarding friction investigations, or requests to make a codebase easier to understand as a whole.
---

# Architecture for comprehension

Assess whether a motivated engineer can build an accurate mental model of the system without holding unnecessary detail in their head.

## Workflow

1. Define the review boundary and the engineer persona whose comprehension matters.
2. Inventory the repository, manifests, entry points, source roots, tests, and architecture documents. Run `bin/architecture-for-comprehension <repo>` for a deterministic first map.
3. Trace the smallest complete execution path that explains the system: entry point, control flow, data transformations, state, side effects, and output.
4. Check whether structure, names, documentation, configuration, and tests describe the same system.
5. Evaluate the dimensions and finding taxonomy in [`references/review-rubric.md`](references/review-rubric.md).
6. Recommend the smallest changes that reduce global cognitive load. Keep local style findings out unless they damage the system model.

## Evidence rules

- Separate observed facts from inference.
- Attach each finding to files, symbols, execution paths, or missing links between them.
- Treat unclear rationale as uncertainty, not proof of poor design.
- Describe tradeoffs under their likely constraints; do not declare an architecture correct from aesthetics alone.
- Raise a question when an important conclusion depends on author intent that the repository cannot reveal.

## Output

Report:

1. A short system model and the path used to derive it.
2. What currently helps comprehension.
3. Findings ordered by cognitive cost, with evidence and confidence.
4. Coherence gaps between code, tests, configuration, and docs.
5. A minimal sequence of improvements, including what not to change casually.

For an independent review, pass [`agents/reviewer.md`](agents/reviewer.md) to a subagent with the repository path and review boundary.
