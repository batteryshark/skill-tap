# FastMCP interaction models

## Choose the narrowest model

| Need | Mechanism |
|---|---|
| Model already knows the value | Typed tool argument |
| Server must ask the person during execution | `ctx.elicit()` |
| Exact human approval for an operation | action elicitation or Approval app provider |
| Structured embedded form | FormInput provider / FastMCP App |
| Clickable alternatives | Choice provider / FastMCP App |
| Drag-and-drop local file | FileUpload provider / FastMCP App |
| Table, chart, dashboard, custom UI | Prefab or custom MCP App |
| Authentication or reusable secret | OAuth / credential flow, not ordinary form data |

Protocol elicitation depends on client capability. Always define the unsupported-client path. Handle accepted, declined, and cancelled results explicitly using APIs documented for the installed FastMCP version; do not preserve compatibility folklore without testing it.

FastMCP Apps add a UI resource and tool metadata. `FastMCPApp` can compose public model-facing tools with private app-only tools. Treat private tool exposure as a security boundary and test the visible catalog.

Approvals must name the target, effect, destination, and material parameters. Bind acceptance to that exact operation and expire or invalidate it when those values change.
