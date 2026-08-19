# Comment quality

Review a comment with its surrounding code, tests, configuration, and relevant history. A polished sentence is not useful when it describes behavior that no longer exists.

## Classify the comment

- **Keep:** preserves non-obvious intent, a binding constraint, a change hazard, a protocol or compatibility quirk, or the reason an apparently simpler approach is unsafe.
- **Rewrite:** contains durable context but is vague, remote from the code it governs, overly historical, or mixed with syntax narration.
- **Replace with code:** explains names, control flow, types, or structure that can be made self-evident without losing necessary context.
- **Move:** belongs in an API contract, decision record, runbook, issue tracker, or user documentation rather than beside the implementation.
- **Delete:** repeats the code, records obsolete behavior, preserves commented-out code, excuses avoidable complexity, or adds process commentary.
- **Add:** surprising behavior or a load-bearing workaround has evidence-backed rationale that the code cannot express safely.
- **Investigate:** asserts intent or constraints that conflict with implementation, tests, configuration, or current documentation.

## Evidence checks

1. Identify the exact claim the comment makes.
2. Verify that claim against nearby behavior and its callers, tests, configuration, and public contract.
3. Ask whether names or structure could carry the same information more accurately.
4. Preserve rationale that would otherwise be lost, especially for security, compatibility, performance, data integrity, and operational hazards.
5. Avoid inventing intent. When rationale matters but cannot be established, state the missing context or ask the narrowest owner question.

## Rewrite shape

Prefer a concise statement of the reason and the protected constraint:

```text
Keep this ordering because <observable dependency or hazard>.
Changing it requires <verification or migration condition>.
```

Do not require every useful comment to follow a template. Return the classification, evidence, reader impact, and smallest action for each material finding.
