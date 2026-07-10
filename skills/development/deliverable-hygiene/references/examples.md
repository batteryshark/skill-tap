# Examples

## Agent Residue

Bad deliverable:

```text
GRIMES_REPORT.md
IMPLEMENTATION_NOTES.md
phase-2-review-output.md
.agent-tool/worktrees/reviewer-001/
.agent-tool.chat-history.md
agent-review-output.md
src/
```

Better during the run:

```text
.agent-work/deliverable-hygiene/2026-06-13-1530/
src/
```

After GREEN, delete the run folder. If a report contains a real architecture decision, distill that decision into an ADR or concise architecture note and delete the report.

## Documentation Sprawl

Bad:

```text
README.md
ARCHITECTURE.md
ARCHITECTURE_FINAL.md
NEW_ARCHITECTURE.md
MIGRATION_COMPLETE.md
```

Better:

```text
README.md
ARCHITECTURE.md
```

Merge durable facts into the canonical docs. Delete status documents that only describe the agent's work.

## Test Theater

Bad:

```text
test_private_parse_step_calls_trim()
test_private_parse_step_calls_split()
test_private_parse_step_sets_tmp_result()
```

Better:

```text
test_parser_accepts_indented_items()
test_parser_rejects_malformed_dates()
```

Keep tests that explain behavior a maintainer cares about. Remove tests that freeze private structure.

## Dead Compatibility

Bad:

```text
if use_legacy_parser:
    return parse_v1(payload)
return parse_v2(payload)
```

When the project is allowed to break and no current caller needs v1, delete the flag, v1 parser, config, tests, and docs together. Do not leave the old path as a fallback.

## Useful Comment

Bad:

```text
# Loop over the users and append active ones.
```

Better:

```text
# Keep suspended accounts out of exports; billing reactivates them asynchronously.
```

The better comment explains a domain hazard that names alone cannot carry.

## Blocked Deletion

If a public endpoint appears unused but there is no caller evidence, block instead of guessing:

```markdown
DH-004 | Legacy API | P1 | routes/billing.py:42 | Block
Need owner confirmation before deleting; no local callers found, but this may be an external contract.
```

Keep this in the run folder, not as a permanent project note, unless the decision becomes durable rationale.
