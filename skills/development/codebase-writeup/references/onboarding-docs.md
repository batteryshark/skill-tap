# Onboarding documentation

Contributor documentation should help a capable newcomer answer three questions quickly: what is this, how do I verify it, and where would I make a safe change?

## Required path

Adapt these elements to the repository instead of creating every possible document:

1. **Purpose and audience:** the problem, primary user or operator, and main runtime.
2. **Prerequisites:** supported runtime or toolchain versions and external services that are genuinely required.
3. **First verification:** the shortest authoritative setup and command sequence that proves the checkout works.
4. **System model:** major components, entry points, data or control flow, stores, and external boundaries.
5. **Change map:** where common changes belong, where tests live, and which contracts or generated artifacts require care.
6. **Operational guidance:** configuration, migrations, troubleshooting, deployment, or runbooks only when relevant to the audience.
7. **Contribution loop:** narrow checks, broader checks, formatting, review expectations, and links to the source of truth.

## Rules

- Follow the repository's existing document layout. Add a new file only when it has a distinct audience and owner.
- Prefer executable commands copied from manifests or automation over prose approximations.
- Label commands as reproduced, documented, or inferred.
- Explain machine-local values with placeholders and never include secret values.
- Link to generated API references, schemas, runbooks, or policies instead of duplicating them.
- Include rationale near a surprising constraint; keep transient project history out.
- Remove stale setup branches when evidence shows they are no longer supported.

## Validation

Check links, command syntax, version claims, path names, and the first verification flow. If a clean-environment run is not authorized or possible, say exactly what was not reproduced.
