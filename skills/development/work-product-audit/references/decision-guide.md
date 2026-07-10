# Decision guide

## Delete

Delete text that answers an objection nobody raised, records internal reasoning, names an old project, narrates the writing process, or repeats nearby content without adding a public contract.

Common candidates:

- defensive contrasts such as “not the whole project” or “not merely”
- thesis scaffolding such as “the point is” or “what really matters”
- task IDs, handoffs, session summaries, local paths, and previous names
- generic conclusions and paragraphs that announce what they are about to say

## Rewrite

Rewrite when the underlying information belongs in public docs but its framing does not. State the behavior, boundary, evidence, or next action directly.

```text
Before: This is not a guarantee that every issue will be detected.
After: The scanner reports matching evidence for human review.
```

## Move internal

Move maintainer-only context to the repository's established internal location when it helps future work but distracts or confuses public readers. Examples include release coordination, unresolved product choices, raw evaluation output, and migration notes that are no longer user instructions.

Do not create a permanent internal document merely to preserve disposable process history.

## Keep

Keep a caveat when it prevents concrete misuse or defines a real contract:

- license, contribution, security, and privacy terms
- threat-model and support boundaries
- output semantics with safety or correctness consequences
- commands that can delete data, execute code, publish changes, or send network traffic

Write the boundary operationally. Prefer “The command deletes untracked files after confirmation” over a paragraph defending what the command is not.

## Review standard

Generated-prose patterns are candidates, not authorship evidence. A finding must explain the reader cost: ambiguity, stale context, unsupported trust, repetition, or an obscured contract.
