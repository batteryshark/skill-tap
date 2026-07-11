---
name: mcp-elicitations
description: "Implement and test FastMCP user elicitation and MCP Apps interaction patterns with explicit accept, decline, cancel, validation, and security behavior."
---

# Build Interactive FastMCP Workflows

1. Decide whether the interaction belongs in ordinary tool arguments, protocol elicitation, or an MCP App. Read [references/interaction-models.md](references/interaction-models.md).
2. Use `ctx.elicit()` for server-initiated, client-mediated structured input during a tool call. Define the response with supported scalar types or a Pydantic model and handle accept, decline, and cancel explicitly.
3. Use an action-only elicitation or the Apps Approval provider for a human checkpoint. A UI confirmation supplements server authorization; it never replaces it.
4. Use `FastMCPApp` or an app-enabled tool when the workflow needs an embedded form, choice, file upload, dashboard, table, or generative UI. Keep private app tools hidden from the model unless they independently belong in the model-facing catalog.
5. Keep credentials out of ordinary elicitation payloads when an OAuth or out-of-band authorization flow is appropriate.
6. Run `bin/mcp-elicitations PATH` to identify interaction code, then test accept, decline, cancel, invalid input, unsupported-client behavior, authorization failure, and replay/idempotency.

Use [agents/interaction-reviewer.md](agents/interaction-reviewer.md) to review trust boundaries and fallback behavior.
