---
name: architecture-for-comprehension
description: Evaluate and map a repository's architecture for coherence, discoverability, predictable execution paths, local reasoning, onboarding friction, accidental complexity, and cognitive load. Use for system-level architecture reviews, newcomer usability probes, repository legibility scorecards, or requests to make a codebase easier to understand as a whole.
---

# Architecture for comprehension

Assess whether a motivated engineer can build an accurate mental model of the system without holding unnecessary detail in their head.

## Workflow

1. Define the review boundary and the engineer persona whose comprehension matters.
2. Inventory the repository, manifests, entry points, source roots, tests, and architecture documents. Run `bin/architecture-for-comprehension <repo>` for a deterministic first map.
3. Build a factual system map of major responsibilities, ownership boundaries, entry points, stores, external services, and generated or operational surfaces. Mark ambiguous ownership rather than guessing.
4. Trace the smallest complete execution path that explains the system: entry point, control flow, data transformations, state, side effects, and output.
5. When onboarding matters, run a bounded newcomer probe with [`references/onboarding-probe.md`](references/onboarding-probe.md). Observe where setup, execution, navigation, and safe-change reasoning break down.
6. Check whether structure, names, documentation, configuration, tests, and runtime behavior describe the same system.
7. Evaluate the dimensions and finding taxonomy in [`references/review-rubric.md`](references/review-rubric.md). Keep an uncertainty register for conclusions whose rationale, ownership, or hazard cannot be established locally.
8. Recommend the smallest changes that reduce global cognitive load. Keep local style findings out unless they damage the system model.

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
4. Coherence gaps and observed onboarding friction.
5. Important unknowns, the evidence needed, and exact owner questions.
6. A minimal sequence of improvements, including what not to change casually.

For an independent review, pass [`agents/reviewer.md`](agents/reviewer.md) to a subagent with the repository path and review boundary. Use [`agents/onboarding-tester.md`](agents/onboarding-tester.md) for a fresh newcomer probe.
