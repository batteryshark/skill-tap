---
name: codebase-writeup
description: Analyze a codebase and produce an evidence-backed technical narrative or onboarding guide covering purpose, stack, architecture, execution paths, data flow, external integrations, setup, safe-change guidance, operational constraints, and important gaps. Use for engineering handoffs, unfamiliar-project explainers, README or contributor documentation, technical writeups, due-diligence summaries, or requests to explain how a repository works.
---

# Codebase writeup

Explain a repository as a working system, not a file list. Lead with the most useful or surprising fact, then show the evidence that supports it.

## Workflow

1. Establish audience, scope, output destination, and deliverable: technical narrative, onboarding guide, handoff, or focused explainer. Confirm whether security or privacy analysis is authorized and relevant.
2. Run `bin/codebase-writeup <repo>` for a neutral profile of languages, manifests, entry-point candidates, documentation, external domains, and large files. It follows Git ignore rules by default; use `--include-ignored` only when ignored material is part of the requested analysis.
3. Read the README and manifests, then trace at least one complete execution path from entry point through state, external effects, and output.
4. Map runtime and build tooling, module ownership, data storage, API boundaries, third-party services, configuration, deployment, and tests.
5. Investigate distinctive behavior from code evidence. Search broadly, then read the surrounding implementation before making a claim.
6. If risk analysis is in scope, describe observable security and privacy boundaries without exposing credential values or asserting exploitable behavior from static hints alone.
7. For contributor-facing documentation, verify discoverable setup, commands, entry points, project structure, and safe-change guidance with [`references/onboarding-docs.md`](references/onboarding-docs.md). Do not claim a command works unless it was reproduced or clearly label it as documented-only.
8. Draft with [`references/writeup-structure.md`](references/writeup-structure.md), omitting sections that genuinely do not apply.
9. Fact-check every concrete claim against files, symbols, configuration, tests, or reproduced behavior.

## Evidence rules

- Cite relative paths and symbols; add line numbers when they are stable and useful.
- Distinguish documented intent, observed implementation, reproduced behavior, and inference.
- State what was read closely, sampled, or left out in large repositories.
- Do not identify a dependency vulnerability from memory. Verify version-sensitive claims with an appropriate current source when requested.
- Report suspected secrets by location and type, never by printing the value.
- Avoid editorial language that outruns the evidence.

## Output

Produce a self-contained writeup for the stated audience. Include a short scope note and confidence limits so a reader knows what the analysis establishes. For onboarding guides, make the first successful verification path and the likely first change discoverable without duplicating reference material already maintained elsewhere.

Use [`agents/researcher.md`](agents/researcher.md) for the evidence pass, [`agents/onboarding-editor.md`](agents/onboarding-editor.md) for contributor documentation, and [`agents/fact-checker.md`](agents/fact-checker.md) for an independent claim audit.
