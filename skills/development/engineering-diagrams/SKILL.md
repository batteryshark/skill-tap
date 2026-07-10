---
name: engineering-diagrams
description: Create or revise evidence-backed engineering diagrams that explain system context, component ownership, data movement, runtime interactions, state transitions, or trust boundaries. Use when a visual model would make architecture, behavior, lifecycle, dependencies, or security boundaries easier to understand or review.
---

# Engineering diagrams

Use a diagram to answer a concrete engineering question, not to reproduce a repository tree. Keep the visual small enough that a reader can challenge its model.

## Workflow

1. State the audience, scope, scenario, and question the diagram must answer.
2. Inspect relevant entry points, modules, interfaces, schemas, stores, external calls, tests, logs, and existing documentation.
3. Choose the smallest useful diagram type with [`references/diagram-types.md`](references/diagram-types.md). Use multiple diagrams only when one view would mix incompatible levels of detail.
4. Scaffold a Markdown and Mermaid starting point when useful:

   ```sh
   bin/engineering-diagrams system --title "Service context"
   bin/engineering-diagrams sequence --title "Request lifecycle" --output docs/request-lifecycle.md
   ```

5. Replace placeholders with evidence-backed nodes, relationships, transitions, guards, and boundaries. Label important inferences instead of presenting them as facts.
6. Add a short legend and evidence notes outside the diagram. Explain omissions that could otherwise mislead the reader.
7. Review the result with [`references/review-checklist.md`](references/review-checklist.md), then verify it against the implementation or an informed maintainer.

## Rules

- Prefer one named scenario or question per diagram.
- Model responsibilities and behavior, not folder names alone.
- Show only detail that changes the reader's understanding.
- Distinguish observed, documented, inferred, and unknown relationships.
- Include failures, alternate paths, guards, or trust crossings when they are central to the question.
- Follow the project's existing diagram format when it has one; otherwise prefer portable Mermaid in Markdown.
- Treat a diagram as a reviewable hypothesis. Update or remove it when the system changes.

## Output

Return the diagram, its question and scope, a compact legend, evidence references, material uncertainties, and the next validation needed.

Use [`agents/cartographer.md`](agents/cartographer.md) for an evidence pass and [`agents/reviewer.md`](agents/reviewer.md) for an independent model critique.
