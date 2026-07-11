---
name: mcp-testing
description: "Test FastMCP servers through direct unit tests, in-memory MCP clients, elicitation handlers, and focused deployed-transport integration checks."
---

# Test a FastMCP Server

1. Run `bin/mcp-testing PATH` to inventory tests and MCP surfaces, then read [references/test-matrix.md](references/test-matrix.md).
2. Test pure domain functions directly without an MCP runtime.
3. Use an in-memory `Client(server)` for component discovery, schema, tool/resource/prompt behavior, errors, structured results, elicitation, authorization, visibility, and task semantics.
4. Mock at the domain adapter boundary, not FastMCP internals. Assert requested side effects and the absence of forbidden side effects.
5. Add subprocess tests only for stdio lifecycle/configuration and HTTP tests only for routing, authentication, proxy, streaming, or deployment integration.
6. Test every destructive or external operation across preview, approve, decline, authorization failure, timeout, retry, and duplicate request cases.
7. Compare the exposed component catalog or fingerprints when compatibility matters.

Use [agents/test-reviewer.md](agents/test-reviewer.md) to identify missing behavioral and security cases.
