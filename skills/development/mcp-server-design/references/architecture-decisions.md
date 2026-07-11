# FastMCP architecture decisions

## Components and composition

- Register a small stable catalog directly.
- Use providers when components come from files, skills, OpenAPI, another MCP server, or another dynamic source.
- Use transforms to namespace, filter visibility/version, reshape tools, expose resources/prompts as tools, or reduce a large catalog with Tool Search.
- Use middleware for request-time concerns such as logging, rate limits, retries, and telemetry.

## Discovery

- Direct tools: lowest conceptual overhead for small catalogs.
- Tool Search: replaces a large catalog with on-demand search.
- Code Mode: lets the model discover and orchestrate tools through sandboxed Python. It reduces catalog and intermediate-result token cost but adds an experimental transform, sandbox dependency, and a new attack surface. Tool side effects remain real even when orchestration code is sandboxed.

## Interaction and output

- Tool arguments are model-supplied inputs.
- Elicitation requests client-mediated user input during a tool call.
- Apps render an interactive UI and can return compact model-facing results.
- Structured output is appropriate for composition and programs; concise content is appropriate for model reading. Many tools should return both where supported.

## Safety

Require an exact preview and fresh approval for irreversible changes, external messages, purchases, permission changes, production mutations, and sensitive-data disclosure. Authentication establishes identity; authorization decides access; approval confirms intent. None substitutes for the others.

Keep secrets in server-side environment, secret stores, or credential providers. Never ask the model to ferry reusable credentials through a normal tool argument.
