# Review rubric

## Finding classes

### Correctness and failure behavior

- Errors are swallowed, misclassified, or stripped of actionable context.
- Fallbacks hide invalid state or convert failures into plausible wrong results.
- Boundary conditions, lifecycle transitions, or cleanup paths are untested.
- Concurrent state ownership, shutdown, cancellation, or lock ordering is unclear.

### Behavioral coverage

- Risky transformations or public contracts lack focused tests.
- Tests assert mocks or private call structure instead of outcomes.
- Flaky, skipped, slow, or order-dependent tests conceal uncertainty.
- Fixtures and helpers hide the condition the test claims to explain.

### Comprehension

- Vocabulary is vague, misleading, inconsistent, or hides side effects.
- One local scope mixes policy, parsing, validation, I/O, mutation, and presentation.
- A model exposes representation while also claiming to protect invariants.
- Comments are stale, nonlocal, repetitive, or compensating for avoidable structure.
- A comment asserts intent that nearby behavior, tests, or current constraints contradict.
- Surprising or hazardous behavior lacks the local rationale needed to change it safely.

### Boundaries and dependencies

- Domain code depends directly on a broad or volatile external API.
- Construction, environment parsing, and framework wiring obscure runtime behavior.
- External data, errors, time, filesystem, or network effects are not normalized at a boundary.
- Abstractions add indirection without reducing coupling or concepts.
- Pass-through layers, unused flexibility, or duplicated policy increase the number of concepts without protecting a supported variation or boundary.

### Consistency and layout

- Code fights the project's formatter, linter, or established idioms.
- Related concepts are far apart or ordered unpredictably.
- Mechanical style churn would dominate the useful change.

## Priority

- **P0:** credible correctness, security, data-loss, or concurrency risk.
- **P1:** significant maintenance cost, hidden failure contract, or missing guardrail around risky behavior.
- **P2:** useful local improvement with bounded reader impact.
- **P3:** preference-level consistency; fix only when adjacent or mechanically enforced.

## Finding shape

```text
Title and priority
Class:
Evidence:
Impact:
Recommended action:
Confidence:
```

Metrics such as file length, nesting, argument count, or duplication are prompts to inspect responsibility. They are not failures by themselves.
