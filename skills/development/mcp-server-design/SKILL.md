---
name: mcp-server-design
description: "Design FastMCP 3 tools, providers, transforms, authorization, background work, output contracts, and human approval boundaries for a production server."
---

# Design a FastMCP Server

1. Inventory users, component count, data sources, trust boundaries, latency, long-running work, and irreversible or external effects.
2. Run `bin/mcp-server-design PATH` to inventory existing FastMCP concerns and read [references/architecture-decisions.md](references/architecture-decisions.md).
3. Keep domain logic library-first. Use providers to source components, transforms to shape the exposed catalog, and middleware for request execution concerns.
4. Prefer ordinary directly exposed tools for a small catalog. Use Tool Search for on-demand discovery, and experimental Code Mode only when server-side Python composition justifies its sandbox and extra dependency.
5. Make output match consumers: typed structured data for programmatic composition, concise content for model reading, and Apps when an interactive UI materially helps. Do not impose a universal text-only rule.
6. Put authorization and visibility on components, authenticate HTTP deployments, keep secrets server-side, and require preview/approval for irreversible, financial, external-communication, permission, or sensitive-data actions.
7. Use task support for genuinely long-running work and explicit timeouts for bounded calls. Keep interactive OAuth and unreliable network work out of startup.
8. Verify schemas, catalog exposure, permissions, output shape, task behavior, and side-effect gates.

Use [agents/architecture-reviewer.md](agents/architecture-reviewer.md) for a threat- and token-budget-aware review.
