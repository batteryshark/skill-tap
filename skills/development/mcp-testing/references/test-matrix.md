# FastMCP test matrix

| Layer | What it proves | Preferred method |
|---|---|---|
| Domain | calculations, validation, adapters | direct unit tests |
| Component | schema, names, results, errors | in-memory `Client(server)` |
| Interaction | accept/decline/cancel, Apps tool visibility | in-memory handlers and catalog assertions |
| Security | authz, sensitive output, side-effect gates | negative and boundary tests |
| Lifecycle | lifespan cleanup, task timeout/cancel | in-memory client plus controlled fakes |
| Stdio | launch command and shutdown | subprocess smoke test |
| HTTP | route, auth, proxy, streaming | deployed integration test |

In-memory usage in current FastMCP is `async with Client(server) as client`. Assert on documented result fields for the installed version. Avoid coupling tests to internal component classes when a client-visible assertion is available.

For upgrades, snapshot the public component inventory and representative schemas or use stable tool fingerprints. A passing tool call does not prove that discovery metadata stayed compatible.
