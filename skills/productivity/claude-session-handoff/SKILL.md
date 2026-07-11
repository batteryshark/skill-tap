---
name: claude-session-handoff
description: "Build a redacted, evidence-backed continuation brief from a Claude Code JSONL transcript. Use when resuming an interrupted agent task, handing work to another agent, or reconstructing objectives, edits, validation, and remaining work."
---

# Build a Claude Session Handoff

1. Identify the Claude Code JSONL transcript, the associated project root, the intended receiving agent, and whether the brief may contain private source or conversation material.
2. Read [references/handoff-evidence.md](references/handoff-evidence.md), then run:

   ```sh
   bin/claude-session-handoff /path/to/session.jsonl \
     --root /path/to/project \
     --redact-session-ids \
     --output /private/path/handoff.md
   ```

3. Keep default redaction enabled. Treat `--no-redact` as an explicit sensitive-data decision, not a convenience flag. Raw tool results are excluded unless `--include-tool-results` is requested because they may be large or secret-bearing.
4. Review the generated objectives, current-state signals, changed-file evidence, commands/results, MCP calls, task events, parse errors, and omitted-item counts against the transcript and current repository state.
5. Add a short verified continuation section stating what is actually complete, what remains, which assumptions are unresolved, and the first safe next action. Do not promote transcript claims to current truth without checking the workspace.
6. Deliver the brief through an approved private channel and retain the source line numbers needed for traceability.

Use [agents/handoff-reviewer.md](agents/handoff-reviewer.md) for an independent evidence and privacy pass.
