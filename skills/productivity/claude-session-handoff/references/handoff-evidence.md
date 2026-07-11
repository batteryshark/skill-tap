# Handoff evidence guide

Claude Code JSONL interleaves user messages, assistant content blocks, tool calls, tool results, local-command wrappers, task events, and metadata. The parser reconstructs chronology and links tool results to calls by ID where possible, but a transcript is not an authoritative snapshot of the filesystem or external systems.

Use source line numbers to resolve ambiguity. Verify changed files with version control or direct reads, and rerun material validation commands when feasible. Treat a command invocation without a captured successful result as attempted, not completed. Treat assistant statements such as "fixed" or "done" as claims requiring evidence.

Default redaction covers common token-bearing URLs, organization UUID labels, email addresses, and secret-like assignments. It cannot recognize every credential, personal detail, source-code secret, or sensitive tool result. Review the output before sharing it, and redact session IDs when they are not needed.

The script currently targets Claude Code's JSONL schema and named tools. Unknown records remain counted, malformed lines are reported, and unsupported tool shapes may lose detail without making the parse fail.
