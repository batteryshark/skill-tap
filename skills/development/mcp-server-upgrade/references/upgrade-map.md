# FastMCP upgrade map

Build the migration from observed behavior and the official upgrade guide for the exact source version.

| Concern | Inspect | Current design direction |
|---|---|---|
| Package provenance | `fastmcp` vs MCP SDK FastMCP | Standalone `fastmcp` package |
| Project config | ad hoc commands, host JSON | `fastmcp.json` plus project metadata |
| Composition | copied decorators, old mounts | providers and namespaced composition |
| Catalog shaping | wrapper tools | transforms, visibility, versions |
| Authorization | global checks only | component authorization plus HTTP auth |
| Context | old imports and implicit globals | documented dependency injection/context APIs |
| Long work | blocking tool call | task configuration with timeouts when supported |
| UI | text-only pseudo forms | protocol elicitation or MCP Apps by need |
| Discovery | expose every schema | direct tools, Tool Search, or experimental Code Mode |
| State | process globals | appropriate storage backend and explicit lifecycle |

Do not infer that a newer feature belongs in the migrated product. Preserve the existing interface first, then propose optional redesign separately.
