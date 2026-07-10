# Review rubric

## Dimensions

### Coherence

The major modules, runtime boundaries, and data ownership rules tell one consistent story. Similar concepts use similar structures; different concepts look intentionally different.

### Discoverability

A newcomer can find entry points, source roots, configuration, tests, and operational boundaries from conventional locations or a short repository map.

### Predictability

Names and structure make control flow, side effects, failure behavior, and extension points unsurprising. Similar operations fail and recover in similar ways.

### Local reasoning

An engineer can change one area without loading unrelated subsystems into memory. Dependencies point in legible directions, and state ownership is explicit.

### Abstraction value

An abstraction removes repetition or hides a stable boundary without scattering the displaced complexity. Count the concepts a reader must learn, not the number of lines saved.

### Documentation alignment

Documentation, tests, manifests, and runtime behavior reinforce the same model. Stale or competing explanations count as a coherence cost.

### Onboarding usability

A capable newcomer can establish purpose, setup, verification commands, primary entry points, ownership, and a safe change location without relying on hidden project history. Required domain knowledge is named; project-specific tribal knowledge is not mistaken for expertise.

## Uncertainty register

For an important claim that cannot be established, record the claim, existing evidence, missing evidence, change risk, and the smallest owner question or experiment that would settle it. Do not convert a low-confidence inference into a negative score.

If the user requests a scorecard, prefer evidence bands such as clear, usable with friction, materially unclear, and not evaluated. Explain each band; avoid a single aggregate number that hides unsupported dimensions.

## Finding taxonomy

- **Intentional tradeoff:** a conscious choice made for a concrete constraint.
- **Historical artifact:** legacy structure retained for compatibility or inertia.
- **Known weakness:** a limitation with a current cost or risk.
- **Deferred decision:** a boundary intentionally left unresolved.
- **Load-bearing weirdness:** surprising behavior that must not be removed casually.
- **Accidental complexity:** complexity with no meaningful current value.

## Confidence

- **High:** directly observed in code, configuration, tests, schemas, or documentation.
- **Medium:** supported by multiple repository signals but not stated directly.
- **Low:** plausible and relevant, with weak local support.
- **Author confirmation required:** important enough that acting on an inference would be risky.

## Finding shape

```text
Title
Dimension and taxonomy:
Evidence:
Mental-model cost:
Smallest improvement:
Confidence:
```
