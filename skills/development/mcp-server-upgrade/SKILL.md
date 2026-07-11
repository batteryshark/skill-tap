---
name: mcp-server-upgrade
description: "Audit and upgrade an existing MCP implementation to current FastMCP 3 patterns while preserving behavior and verifying protocol compatibility."
---

# Upgrade a FastMCP Server

1. Record the installed `fastmcp`, `mcp`, Python, and deployment versions plus the server's existing component inventory and representative outputs.
2. Run `bin/mcp-server-upgrade PATH` for a static migration inventory, then read [references/upgrade-map.md](references/upgrade-map.md).
3. Separate framework migration from product redesign. Preserve observable names, schemas, errors, auth requirements, and effects unless the user requested a breaking change.
4. Migrate imports, configuration, composition, context access, and transport setup in small groups. Replace deprecated patterns with current providers, transforms, component authorization, visibility, versioning, storage, or tasks only where they solve an actual requirement.
5. Treat Code Mode and Apps as opt-in product capabilities, not automatic upgrade steps.
6. Compare pre/post component catalogs and run direct, in-memory, and deployment smoke tests.

Ask [agents/migration-reviewer.md](agents/migration-reviewer.md) to inspect compatibility evidence before release.
