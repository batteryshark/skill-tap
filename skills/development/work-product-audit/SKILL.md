---
name: work-product-audit
description: Audit repositories and public documentation for internal notes, defensive explanations, unexplained assertions, stale project residue, hidden assumptions, and generated-sounding meta commentary. Use when scanning launch material, cleaning public prose, or deciding which reasoning belongs outside the finished deliverable.
---

# Work-product audit

Keep a repository readable as finished work rather than a transcript of how the work was produced.

## Workflow

1. Identify the public surface: root docs, package documentation, `docs/`, examples, schemas, user-facing prompts, and CLI help. Exclude version-control data, caches, dependencies, generated output, internal notes, and agent scratch unless the request includes them.
2. Run the candidate scanner:

   ```sh
   bin/work-product-audit <repo-or-file>
   ```

3. Review every hit in context. The scanner reports candidates, not verdicts.
4. Classify each item with [`references/decision-guide.md`](references/decision-guide.md): delete, rewrite, move internal, or keep.
5. Edit with a deletion bias. Turn useful defensive or meta framing into a direct statement of behavior.
6. Re-run the scanner and the repository's link, style, or documentation checks.

## Evidence rules

- Tie every recommendation to the audience and maintenance cost.
- Preserve operational boundaries that prevent concrete misuse.
- Distinguish an unsupported assurance from a claim backed by nearby evidence.
- Search for old names, task identifiers, local paths, session residue, and provider notes before publication.
- Treat patterns associated with generated prose as review cues, never proof of authorship.

## Report

Group changes by delete, rewrite, move, and intentional keep. Explain any remaining candidate that could surprise a later auditor.

For an independent read-only pass, use [`agents/auditor.md`](agents/auditor.md).
