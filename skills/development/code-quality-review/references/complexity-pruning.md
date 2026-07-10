# Complexity pruning

Use this lens when the request is to simplify, remove over-engineering, or reduce maintenance surface. The goal is fewer concepts and failure modes, not fewer lines at any cost.

## Review leads

- Custom parsing, scheduling, retrying, caching, validation, or collection logic duplicates a reliable standard-library or platform capability.
- A dependency is used for a narrow operation already available in the project or runtime.
- An interface, factory, registry, adapter, or wrapper has one consumer and adds indirection without protecting a real boundary.
- Configuration, flags, extension points, or generic parameters have no active variation and no supported external contract.
- Two layers repeat the same policy, validation, or data translation.
- Dead branches, obsolete compatibility paths, unused exports, or abandoned experiments remain reachable only in theory.
- A file or module exists solely to rename and forward calls without creating ownership or isolation value.

These are prompts to investigate, not automatic findings. A single implementation can still protect a volatile boundary, and a wrapper can encode observability, policy, test control, or compatibility.

## Evidence before a cut

1. Find all static references and likely dynamic or reflective use.
2. Read tests, public documentation, configuration, serialization, and plugin contracts.
3. Identify the responsibility the structure claims to own.
4. State what behavior and operational property must remain.
5. Name the smaller replacement and how to verify equivalence.
6. Mark uncertain historical or compatibility behavior for owner confirmation.

## Finding shape

```text
Opportunity:
Evidence:
Current concept or maintenance cost:
Smallest replacement:
Protected behavior:
Verification:
Confidence:
```

Do not recommend a cut when the replacement merely hides complexity, weakens failure handling, obscures domain vocabulary, or makes a future change only hypothetically easier.
