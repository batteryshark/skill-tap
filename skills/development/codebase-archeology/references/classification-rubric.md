# Classification rubric

## Active candidate

The work has clear current value and a plausible maintenance path. Identify the canonical variant, current users, missing verification, and minimum work needed to make it legible or runnable.

## Reference

The work is useful for ideas, protocols, research, compatibility, or provenance but is not a strong active-maintenance candidate. Preserve enough context to explain why it matters and how to inspect it safely.

## Merge or deduplicate

The unit overlaps another candidate. Exact hash matches can be deduplicated confidently after ownership approval. Near-duplicates require structural or semantic comparison and a decision about which history or unique behavior survives.

## Preserved artifact

The original form has historical, evidentiary, interoperability, or reproducibility value. Preserve it immutably or with checksums, even when a port or rewrite becomes the active version.

## Retire candidate

The work appears superseded, empty, generated, or without recoverable value. Mark it for owner review; do not delete it during discovery.

## Evidence fields

For each classification record:

- relative path and project boundary
- observed purpose and entry points
- language, toolchain, and platform assumptions
- relationship to neighboring variants
- tests or runtime evidence
- unique artifacts or decisions
- confidence and owner question
