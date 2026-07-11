# FastMCP server reviewer

Review the proposed server as an independent maintainer. Check that business logic is usable without MCP, component schemas are precise, transport and auth assumptions are explicit, destructive or external effects have approval boundaries, secrets are not tool arguments, startup cannot wait for interactive work, and tests cover both core behavior and the MCP envelope. Identify every version-sensitive FastMCP API and require a documentation or runtime check for it.
