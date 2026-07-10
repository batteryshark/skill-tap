---
name: codebase-archeology
description: Investigate and preserve archived, inherited, abandoned, or poorly understood codebases by mapping project variants, toolchains, build assumptions, duplicate artifacts, historical value, and modernization options. Use for legacy project intake, repository preservation, compatibility work, build recovery, false-start comparison, or deciding what should be kept, merged, archived, or retired.
---

# Codebase archeology

Turn an old or messy project collection into a defensible preservation decision without destroying evidence or rewriting history prematurely.

## Workflow

1. Confirm the target and start read-only.
2. Run `bin/codebase-archeology <target>` to inventory languages, manifests, archives, binary artifacts, and exact duplicate candidates.
3. Map entry points, build systems, source roots, tests, platform assumptions, third-party code, generated output, experiments, forks, and neighboring project variants.
4. Classify each meaningful unit with [`references/classification-rubric.md`](references/classification-rubric.md): active candidate, reference, merge/deduplicate, preserved artifact, or retire candidate.
5. Produce a working map that separates observation, inference, and author confirmation. Treat it as scratch unless the user asks for a durable report.
6. If curation is authorized, follow [`references/preservation-workflow.md`](references/preservation-workflow.md). Preserve behavior and provenance before modernization.
7. Validate build or runtime claims in the narrowest available environment. Distinguish reproduced behavior from plausible reconstruction.

## Rules

- Never delete, quarantine, rewrite, format, or initialize version control during discovery.
- Hash equality proves identical bytes; similar names, sizes, or structures are only comparison leads.
- Keep original artifacts when their historical or evidentiary value matters, even if a modern rewrite becomes the maintained path.
- Separate first-party work from vendored dependencies, generated outputs, archives, binaries, and unrelated clutter.
- Prefer relative paths in durable documentation. Absolute paths belong only in transient environment diagnostics.
- Do not assume an obsolete language or build system should be rewritten. State preservation, emulation, porting, and rewrite tradeoffs.
- Require explicit approval before destructive cleanup or moves that can break external references.

## Report

State target, project map, classifications, exact duplicates, likely relationships, reproduced build/runtime evidence, preservation recommendation, and decisions requiring the owner.

Use [`agents/investigator.md`](agents/investigator.md) for a read-only mapping pass and [`agents/validator.md`](agents/validator.md) to challenge preservation conclusions.
