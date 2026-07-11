---
name: mcp-server-create
description: "Scaffold and verify a portable FastMCP 3 server project with declarative configuration, library-first logic, tests, and safe transport defaults."
---

# Create a FastMCP Server

1. Clarify the server boundary, consumers, transport, authentication owner, side effects, and whether the core logic must also serve a CLI or library.
2. Read [references/current-fastmcp.md](references/current-fastmcp.md) and pin a tested FastMCP 3 minor range; do not silently copy version-sensitive APIs from memory.
3. Run `bin/mcp-server-create NAME --target-dir PATH` to generate a library-first project with `fastmcp.json`, tests, and explicit stdio defaults.
4. Replace the example operation with typed core functions. Keep FastMCP decorators, context, auth, and transport concerns in the thin server envelope.
5. Add only the interaction layer the product needs: protocol elicitation for client-mediated input, Apps for embedded UI, or ordinary tool arguments for model-supplied data.
6. Run the generated unit and in-memory protocol tests, inspect the component catalog, and exercise the real deployment transport only after local behavior is correct.

Use [agents/server-reviewer.md](agents/server-reviewer.md) for an independent boundary and safety review.
