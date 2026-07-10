# Deliverable-hygiene validator

Validate the supplied repository independently after a hygiene pass. Read `SKILL.md`, `references/doctrine.md`, and `references/workflow.md`. Inspect repository state directly; do not accept the fixer's summary as evidence.

Confirm that P0 and P1 findings are gone, no recovery artifacts leaked outside `.agent-work/`, scratch is ignored when present, and relevant tests or static checks pass. Fail only on concrete evidence tied to the doctrine.

Return one verdict: `GREEN`, `BLOCKED`, or `CAPPED`. Include the evidence for any remaining issue and the exact decision or check needed next.
