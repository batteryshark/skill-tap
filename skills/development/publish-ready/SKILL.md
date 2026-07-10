---
name: publish-ready
description: Prepare a repository for public release by removing development residue and dead paths, consolidating documentation, tightening generated-sounding prose, checking for secrets and local-machine references, and proving that surviving quickstarts and checks work. Use before open-sourcing, sharing, handing off, demonstrating, or releasing a project.
---

# Publish ready

Turn a working repository into a coherent public artifact for a stranger deciding whether to trust and use it.

## Guardrails

Work from version control on a reviewable branch or equivalent recovery point. If the workspace has no version control, stop and establish one before an aggressive cleanup.

Verify before deleting an ambiguous file. Fixtures, generated inputs, and data files can resemble junk. Run relevant checks after each meaningful batch of removals.

## Process

### 1. Orient

Run `bin/publish-ready <repo>` and treat the output as leads. Read the README, manifests, entry points, tests, and release machinery. Write a one-sentence private answer to: what is this, and who uses it?

Identify the load-bearing surface before editing: shipped code, real tests and fixtures, license, CI, lockfiles, and any document that defines a public contract.

### 2. Cut

Remove development detritus, dead code, abandoned scaffolding, redundant docs, stale references, and generated output that belongs in ignore rules. Search for references before deleting anything ambiguous.

Keep one source of truth per topic. Remove obsolete compatibility paths only when repository evidence or explicit scope makes the break safe.

### 3. Make the layout legible

A new reader should understand the project, audience, quickstart, and directory map in about a minute. Use conventional locations and names. Prefer one strong root README over overlapping orientation documents.

### 4. Humanize prose

Read [`references/prose-humanizer.md`](references/prose-humanizer.md). Tighten every surviving public document and comment: cut hedges, marketing adjectives, fake contrasts, repetitive summaries, decorative emphasis, and comments that narrate syntax.

### 5. Prove the repository

- Run the build, tests, linters, formatters, and repository-specific validation that actually exist.
- Execute quickstart commands and documentation examples as written.
- Check for secrets, environment files, absolute local paths, debt markers, and references to deleted files.
- Confirm that README claims match current behavior.
- Move aspirations to the project's issue tracker instead of presenting them as shipped features.

### 6. Report

Summarize what was removed, what was rewritten, checks that passed, skipped checks with reasons, and decisions left to the owner. Keep the change reversible and reviewable.

Use [`agents/reviewer.md`](agents/reviewer.md) for an independent final pass.

## Preserve by default

Do not remove licenses, meaningful history, genuine tests and fixtures, CI, ignore rules, lockfiles, or the actual design specification merely to shrink the repository. A smaller broken repository is not publish-ready.
