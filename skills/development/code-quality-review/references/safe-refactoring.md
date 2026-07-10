# Safe refactoring

## Establish the guardrail

Identify public APIs, wire formats, persisted data, configuration keys, reflection, generated code, framework conventions, and external callers before moving or renaming them. Find the tests that protect observable behavior. Add characterization tests when important behavior is unclear.

## Improve in small steps

Prefer this order when it fits the evidence:

1. Clarify misleading names and local variables.
2. Extract coherent concepts that interrupt the main flow.
3. Separate policy from parsing, validation, I/O, and presentation.
4. Move behavior next to the state or boundary that owns it.
5. Consolidate duplicated knowledge after the common concept is clear.
6. Remove dead paths only after searches and checks show they are not load-bearing.

Do not mix a behavior change with a large structural rewrite unless the request requires both.

## Verify repeatedly

- Run focused tests after each coherent step.
- Use type checks and compiler-backed renames when available.
- Inspect the diff for accidental changes to error text, ordering, timing, serialization, and side effects.
- Re-read the changed path from its caller's perspective.

## Stop conditions

Stop and request direction when the next step would change a public contract, persisted data, compatibility behavior, user-visible semantics, or an area whose current behavior cannot be established safely.
