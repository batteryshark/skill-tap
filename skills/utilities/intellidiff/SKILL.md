---
name: intellidiff
description: Compare files or directory trees, detect exact duplicate files, calculate SHA-256 checksums, normalize text for semantic comparison, and read targeted line ranges. Use when determining whether artifacts are identical, finding orphaned or changed files between folders, deduplicating collections, inspecting backups, or explaining content differences without modifying the inputs.
---

# IntelliDiff

Use deterministic, read-only comparisons before making deduplication or merge decisions.

## Commands

Run the portable entry point:

```sh
bin/intellidiff hash FILE
bin/intellidiff file LEFT RIGHT
bin/intellidiff file LEFT RIGHT --smart --ignore-whitespace --ignore-blank
bin/intellidiff folders LEFT RIGHT
bin/intellidiff duplicates FOLDER
bin/intellidiff lines FILE --start 20 --end 40 --context 3
```

Read [`references/reference.md`](references/reference.md) for normalization semantics, hidden-file behavior, JSON output, and exit codes.

## Workflow

1. Choose exact file comparison for byte identity and smart comparison only when specific textual differences should be ignored.
2. Compare directory trees before deciding which side is canonical. Review same-path changes separately from left-only and right-only files.
3. Use duplicate detection to find exact content groups. Hash equality is strong evidence for identical content, not authorization to delete a copy.
4. Inspect metadata, neighboring files, references, and provenance before moving or removing duplicates.
5. Report the comparison mode and every normalization applied so the meaning of “same” is explicit.

## Rules

- Never modify, move, or delete inputs.
- Use SHA-256 rather than timestamps, names, or CRC checksums for identity grouping.
- Do not call normalized text byte-identical.
- Hidden files are skipped by default except when `--include-hidden` is explicit; `.git` and common dependency/build caches remain excluded.
- Symlinks are not followed.
- Treat unreadable files and decode failures as explicit errors, not silent differences.

Use [`agents/analyst.md`](agents/analyst.md) when the comparison needs a human-readable merge or deduplication recommendation.
