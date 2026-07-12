---
name: skill-refine
description: Audit and improve a portable skill for contract compliance, triggering, progressive disclosure, script correctness, portability, safety, and verification. Use for skill reviews, pre-publication checks, broken-skill diagnosis, quality scoring, or modernizing an older package to the Skill Tap contract.
---

# Refine a Portable Skill

1. Run `bin/skill-refine PATH` for objective structural findings.
2. Read [references/review-rubric.md](references/review-rubric.md) and inspect every referenced file and executable path.
3. Run each script and primary `bin/` command against representative and boundary fixtures.
4. Compare description claims with actual behavior; prioritize misleading triggers and broken execution over style.
5. Apply fixes without adding filler, vendor-specific metadata, or hidden sibling dependencies.
6. Re-run the package validator and forward-test consequential workflows in fresh context.

Use [agents/skill-reviewer.md](agents/skill-reviewer.md) for an independent evidence-based pass.
