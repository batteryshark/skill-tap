# Current FastMCP baseline

FastMCP changes quickly. Before generating code, verify names and signatures against the installed version and the current official documentation at `gofastmcp.com`.

## Baseline architecture

- Treat servers, Apps, and clients as distinct surfaces.
- Use `fastmcp.json` for portable declarative server configuration; keep dependency metadata in `pyproject.toml`.
- Prefer Streamable HTTP for remote servers and stdio for local host-launched servers. SSE is legacy compatibility work.
- Keep domain operations in ordinary Python modules and the FastMCP server as an envelope.
- Use providers to source components and transforms to reshape what clients see.
- Authentication is an HTTP concern; stdio inherits the launching user's boundary.
- Use MCP tasks for long-running operations only when the client/server combination supports them.
- Code Mode is experimental and requires the `code-mode` extra.
- Apps require the `apps` extra and a host that supports the MCP Apps extension.

## Generated-project verification

1. Install from the lockfile in an isolated environment.
2. Import the server without network access or prompts.
3. Inspect/list components.
4. Run direct domain tests and in-memory client tests.
5. Run the configured stdio server and, if applicable, the HTTP deployment.
6. Confirm no credential, private path, host-specific executable, or user-specific host configuration was embedded.
